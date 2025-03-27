import requests
import json
import os
from datetime import datetime, timezone

# with open('move_0.json', 'w') as f:
#             content = json.dumps(response, indent=2)
#             f.write(content)

basedir = os.path.dirname(__file__)

with open(os.path.join(basedir, 'token.txt'), 'r') as f:
    token = f.read()

headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }


# Lists to display different info about a character
skills = [
    'mining_level', 'mining_xp', 'mining_max_xp', 'woodcutting_level',
    'woodcutting_xp', 'woodcutting_max_xp', 'fishing_level',
    'fishing_xp', 'fishing_max_xp', 'weaponcrafting_level',
    'weaponcrafting_xp', 'weaponcrafting_max_xp',
    'gearcrafting_level', 'gearcrafting_xp', 'gearcrafting_max_xp',
    'jewelrycrafting_level', 'jewelrycrafting_xp',
    'jewelrycrafting_max_xp', 'cooking_level', 'cooking_xp',
    'cooking_max_xp', 'alchemy_level', 'alchemy_xp', 'alchemy_max_xp',
]

stats = [
    'haste', 'critical_strike', 'wisdom', 'prospecting',
    'attack_fire', 'attack_earth', 'attack_water', 'attack_air',
    'dmg', 'dmg_fire', 'dmg_earth', 'dmg_water', 'dmg_air', 'res_fire',
    'res_earth', 'res_water', 'res_air',
]

char_info_list = [
    'level', 'xp', 'max_xp', 'gold', 'hp', 'max_hp', 'speed',
    'x', 'y', 'task', 'task_type', 'task_progress', 'task_total',
    'inventory_max_items', 'cooldown', 'cooldown_expiration',
]

clothes = [   
    'weapon_slot', 'rune_slot', 'shield_slot', 'helmet_slot', 'body_armor_slot',
    'leg_armor_slot', 'boots_slot', 'ring1_slot', 'ring2_slot',
    'amulet_slot', 'artifact1_slot', 'artifact2_slot',
    'artifact3_slot', 'utility1_slot', 'utility1_slot_quantity',
    'utility2_slot', 'utility2_slot_quantity', 'bag_slot', 
]


class Character:
    def __init__(self, name):
        self.name = name
        self.npc_code = ''

        self.char_info = {}
        self.get_char_info()

        self.skills = skills
        self.char_info_list = char_info_list
        self.stats = stats
        self.clothes = clothes
        self.npc = None

        with open(os.path.join(basedir, 'json', 'items.json'), 'r') as f:
            self.items = json.load(f)

        with open(os.path.join(basedir, 'json', 'monsters.json'), 'r') as f:
            self.monsters = json.load(f)
        
        with open(os.path.join(basedir, 'json', 'bank.json'), 'r') as f:
            self.bank = json.load(f)

        with open(os.path.join(basedir, 'json', 'maps.json'), 'r') as f:
            self.maps_data = json.load(f)

    def get_char_info(self):
        url = f"https://api.artifactsmmo.com/characters/{self.name}"
        response = requests.get(url, headers=headers).json()
        self.char_info = response['data']

    def _json(self, response):
        if response.status_code == 200:
            return response.json()
        else:
            data, error = {}, []
            response = response.json()
            error.append(f"Code: {response['error']['code']}")
            error.append(f"{response['error']['message']}")
            data['data'] = error
            data['error'] = 'error'
            return data

    def _get(self, action):
        url = f"https://api.artifactsmmo.com/{action}"
        response = requests.get(url, headers=headers)
        return self._json(response)

    def _post(self, action, payload=None):
        url = f"https://api.artifactsmmo.com/my/{self.name}/action/{action}"
        response = requests.post(url, json=payload, headers=headers)
        return self._json(response)
              
    def move(self, info):
        answer = {}
        payload = {"x": info['x'], "y": info['y']}
        response = self._post('move', payload=payload)
        if 'error' in response:
            return response
        else:
            self.char_info = response['data']['character']

            data = []
            data.append('--Move--')
            data.append(f"Cooldown: {str(response['data']['cooldown']['total_seconds'])}.")
            data.append(f"Moved to: {response['data']['destination']['name']}.")
            if response['data']['destination']['content']:
                answer['type'] = response['data']['destination']['content']['type']
                answer['code'] = response['data']['destination']['content']['code']
                data.append(f"Content type: {str(response['data']['destination']['content']['type'])}.")
                data.append(f"Content: {str(response['data']['destination']['content']['code'])}.")
                if response['data']['destination']['content']['type'] == 'npc':
                    self.npc_code = response['data']['destination']['content']['code']
            answer['data'] = data
            answer['name'] = response['data']['destination']['name']
            cooldown = response['data']['cooldown']['total_seconds']
            answer['cooldown'] = cooldown
            return answer

    def fight(self, info):
        answer = {}
        response = self._post('fight')
        if 'error' in response:
            return response
        else:
            self.char_info = response['data']['character']

            data = []
            data.append('--Fight--')
            data.append(f"Cooldown: {str(response['data']['cooldown']['total_seconds'])}.")
            data.append(f"XP gained: {response['data']['fight']['xp']}.")
            data.append(f"Gold collected: {response['data']['fight']['gold']}.")
            for drop in range(len(response['data']['fight']['drops'])):
                drop_text = ''
                drop_text += f"Drop: {response['data']['fight']['drops'][drop]['code']} \n"
                drop_text += f"Quantity: {response['data']['fight']['drops'][drop]['quantity']}"
                data.append(drop_text)
            data.append(f"Turns: {response['data']['fight']['turns']}")
            data.append(f"Result: {response['data']['fight']['result']}")
            answer['data'] = data
            cooldown = response['data']['cooldown']['total_seconds']
            answer['cooldown'] = cooldown
            return answer

    def logs(self, info):
        answer, data = {}, []
        response = self._get('my/logs')['data']
        number_of_logs = len(response)
        if number_of_logs > 50:
            number_of_logs = 50
        for log in range(number_of_logs):
            text = f'{log}. --' + response[log]['type'].capitalize() + '--\n'
            text += f"Description: {response[log]['description']}\n"
            if response[log]['type'] == 'rest':
                text += f"HP restored: {response[log]['content']['hp_restored']}\n"
            if response[log]['type'] == 'fight':
                text += f"Result: {response[log]['content']['fight']['result']}\n"
                text += f"Turns: {response[log]['content']['fight']['turns']}\n"
                text += f"Monster: {response[log]['content']['fight']['monster']}\n"
                text += f"XP gained: {response[log]['content']['fight']['xp_gained']}\n"
                text += "Drops: \n"
                for key, value in response[log]['content']['drops'].items():
                    text += f"  {key}: {value}\n"
            data.append(text)
        answer['data'] = data
        return answer
    
    def rest(self, info):
        answer = {}
        response = self._post('rest')
        if 'error' in response:
            return response
        else:
            self.char_info = response['data']['character']

            data = []
            data.append('--Rest--')
            data.append(f"Cooldown: {str(response['data']['cooldown']['total_seconds'])} sec.")
            data.append(f"Hp restored: {response['data']['hp_restored']}.")
            answer['data'] = data
            cooldown = response['data']['cooldown']['total_seconds']
            answer['cooldown'] = cooldown
            return answer
    
    def map(self, info):
        answer = {}
        response = self._get('/'.join(['maps', info['x'], info['y']]))
        if 'error' in response:
            return response
        else:
            data = []
            data.append('--Map here--')
            data.append(f"Map name: {response['data']['name']}.")
            data.append(f"X coordinate: {response['data']['x']}")
            data.append(f"Y coordinate: {response['data']['y']}")
            if response['data']['content']:
                answer['type'] = response['data']['content']['type']
                answer['code'] = response['data']['content']['code']
                data.append(f"Content type: {str(response['data']['content']['type'])}.")
                data.append(f"Content: {str(response['data']['content']['code'])}.")
                if response['data']['content']['type'] == 'npc':
                    self.npc_code = response['data']['content']['code']
            answer['data'] = data
            answer['name'] = response['data']['name']
            return answer

    def gathering(self, info):
        answer = {}
        response = self._post('gathering')
        if 'error' in response:
            return response
        else:
            self.char_info = response['data']['character']

            data = []
            data.append('--Gathering--')
            data.append(f"Cooldown: {str(response['data']['cooldown']['total_seconds'])}.")
            data.append(f"Gathering xp gained: {response['data']['details']['xp']}.")
            for item in range(len(response['data']['details']['items'])):
                item_text = ''
                item_text += f"Drop: {response['data']['details']['items'][item]['code']} \n"
                item_text += f"Quantity: {response['data']['details']['items'][item]['quantity']}"
                data.append(item_text)
            answer['data'] = data
            cooldown = response['data']['cooldown']['total_seconds']
            answer['cooldown'] = cooldown
            return answer

    def craft(self, info):
        answer, data, text = {}, [], ''
        payload = {"code": info['text'], "quantity": info['quantity']}
        response = self._post('crafting', payload=payload)
        if 'error' in response:
            return response
        else:
            response = response['data']
            self.char_info = response['character']
            
            data.append('--Crafting--')
            data.append(f"Cooldown: {str(response['cooldown']['total_seconds'])}.")
            for k, v in response['details'].items():
                text += f"{k}: {v}\n"
            data.append(text)
            answer['data'] = data
            cooldown = response['cooldown']['total_seconds']
            answer['cooldown'] = cooldown
            return answer
    
    def view_info_about_char(self, info):
        list_to_view = info['button_name']
        if list_to_view == 'char info':
            list_to_view = 'char_info_list'
        answer, data, text = {}, [], ''
        if list_to_view == 'inventory':
            data.append(f"Max items can be in inventory: {self.char_info['inventory_max_items']}")
            quantity = 0
            for i in range(len(self.char_info['inventory'])):
                if self.char_info['inventory'][i]['quantity'] != 0:
                    text = 'Slot: ' + str(self.char_info['inventory'][i]['slot'])
                    text += '  ' + self.char_info['inventory'][i]['code']
                    text += ': ' + str(self.char_info['inventory'][i]['quantity'])
                    quantity += self.char_info['inventory'][i]['quantity']
                    item = self.char_info['inventory'][i]['code']
                    for i in range(len(self.items)):
                        if self.items[i]['code'] == item:
                            if self.items[i]['type'] in ('weapon', 'shield', 'helmet',
                                'body_armor', 'leg_armor', 'boots', 'ring', 'amulet',
                                'artifact'):
                                text += f"\n           lvl: {self.items[i]['level']}"
                                attack = []
                                dmg = []
                                res = []
                                for eff in range(len(self.items[i]['effects'])):
                                    values = list(self.items[i]['effects'][eff].values())
                                    for val in values:
                                        if 'attack' in str(val):
                                            attack.append(val.replace('attack_', ''))
                                        if 'dmg' in str(val):
                                            dmg.append(val.replace('dmg_', ''))
                                        if 'res' in str(val):
                                            res.append(val.replace('res_', ''))
                                if len(attack) != 0:
                                    text += f"\n           attack: {', '.join(attack)}"
                                if len(dmg) != 0:
                                    text += f"\n           dmg: {', '.join(dmg)}"
                                if len(res) != 0:
                                    text += f"\n           res: {', '.join(res)}"
                    data.append(text)
            data.insert(1, f"Items in inventory: {quantity}\n")
        elif list_to_view == 'bank':
            data.append('--Items in bank--')
            data.append(f"Gold in bank: {self.bank['gold']}")
            for i in range(len(self.bank['items'])):
                    text = f"{i+1}: {self.bank['items'][i]['code'].capitalize()}: "
                    text += f"{self.bank['items'][i]['quantity']}"
                    data.append(text)
        elif list_to_view == 'clothes':
            for item in self.clothes:
                text = f'{item.capitalize()}:  {str(self.char_info[item]).capitalize()}'
                for i in range(len(self.items)):
                    if self.items[i]['code'] == self.char_info[item]:
                        text += f"  {self.items[i]['level']}"
                data.append(text)
        else:
            list_to_view = getattr(self, list_to_view)
            for item in list_to_view:
                text = f'{item}'.capitalize() + ': '
                text += str(self.char_info[item])
                data.append(text)
        answer['data'] = data
        return answer
    
    def equip_unequip(self, info):
        action = info['button_name']
        quantity = info['quantity']
        item_info = info['text']
        answer = {}
        slot = ''
        item_info = item_info.split()
        item = item_info[0]
        if len(item_info) > 1:
            slot = item_info[1]
        else:
            for i in range(len(self.items)):
                if item == self.items[i]['code']:
                    slot = self.items[i]['type']
        payload = {"code": item, 'slot': slot, "quantity": quantity}
        response = self._post(action, payload=payload)
        if 'error' in response:
            return response
        else:
            self.char_info = response['data']['character']

            data = []
            text = f"--{response['data']['cooldown']['reason'].capitalize()}ed--\n"
            text += f"Name: {response['data']['item']['name']}\n"
            text += f"Item code: {response['data']['item']['code']}\n"
            text += f"Slot: {response['data']['slot']}"
            data.append(text)
            answer['data'] = data
            cooldown = response['data']['cooldown']['total_seconds']
            answer['cooldown'] = cooldown
            return answer
    
    def get_crafted_items_by_skills(self, info):
        answer, data = {}, []
        skill = info['text']
        if skill == '':
            data.append('Type needed skill for search')
            answer['data'] = data
            return answer
       
        text = f'--All recipeis for {skill} skill--\n\n'
        for i in range(len(self.items)):
            if self.items[i]['craft'] and self.items[i]['craft']['skill'] == skill:
                text += f"Name: {self.items[i]['name']}\n"
                text += f"Code: {self.items[i]['code']}\n"
                text += f"Level: {self.items[i]['level']}\n"
                text += f"Subtype: {self.items[i]['type']}\n"
                if self.items[i]['description']:
                    text += f"Description: {self.items[i]['description']}\n"
                text += f"Effects: {self.items[i]['effects']}\n"
                text += f"Craft: level {self.items[i]['craft']['level']}, Items: \n"
                for item in self.items[i]['craft']['items']:
                    text += f"{self.items[i]['craft']['items']} \n"
                text += f"Tradeable: {self.items[i]['tradeable']}\n\n"
        data.append(text)
        answer['data'] = data
        return answer
    
    def get_item_info(self, info):
        item = info['text']
        answer, data = {}, []
        crafted_items = [f"\nItems can be crafted with {item}:"]
        if item == '':
            data.append('Type item code to get info.')
            answer['data'] = data
            return answer
        
        for i in range(len(self.items)):
            if self.items[i]['code'] == item:
                for key, value in self.items[i].items():
                    text = f"{key}: {value}"
                    data.append(text)
        for i in range(len(self.items)):
            if self.items[i]['type'] != 'resource' and self.items[i]['craft']:
                for j in range(len(self.items[i]['craft']['items'])):
                    if self.items[i]['craft']['items'][j]['code'] == item:
                        crafted_items.append(
                            f"  {self.items[i]['code']} - level: {self.items[i]['level']}")
        if len(crafted_items) > 1:
            crafted_items = tuple(crafted_items)
            data.extend(crafted_items)
        answer['data'] = data
        return answer
    
    def get_monster_info(self, info):
        monster = info['text']
        attack_resist_list = ['attack_fire', 'attack_earth',
            'attack_water', 'attack_air', 'res_fire', 'res_earth',
            'res_water', 'res_air']

        answer, data, text = {}, [], ''
        if monster == '':
            data.append('Type monster name to get info.')
            answer['data'] = data
            return answer
        
        for i in range(len(self.monsters)):
            if self.monsters[i]['code'] == monster:
                text = f"Name: {self.monsters[i]['name']}\n"
                text += f"Code: {self.monsters[i]['code']}\n"
                text += f"Level: {self.monsters[i]['level']}\n"
                text += f"HP: {self.monsters[i]['hp']}\n"
                text += f"Min gold: {self.monsters[i]['min_gold']}\n"
                text += f"Max gold: {self.monsters[i]['max_gold']}\n"
                for j in attack_resist_list:
                    if self.monsters[i][j]:
                        text += f"{j.capitalize()}: {self.monsters[i][j]}\n"
                text += f"Drops: \n"
                for drop in range(len(self.monsters[i]['drops'])):
                    text += f"  --{drop+1}--\n"
                    for key, value in self.monsters[i]['drops'][drop].items():
                        text += f"    {key}: {value}\n"                    
                data.append(text)
        answer['data'] = data
        return answer
    
    def task_action(self, info):
        # Accept new task, cancel task, complete task
        # Exchange task coins on items
        action = info['button_name']
        action = action.replace('task', '').strip()
        answer, data, text = {}, [], ''
        response = self._post(f'task/{action}')
        if 'error' in response:
            return response
        response = response['data']
        self.char_info = response['character']
        if action == 'new':
            text = f"Code: {response['task']['code']}\n"
            text += f"Type: {response['task']['type']}\n"
            text += f"Total: {response['task']['total']}\n"
            text += f"Rewards:\n"
            text += f"  Gold: {response['task']['rewards']['gold']}\n"
            for i in range(len(response['task']['rewards']['items'])):
                for k, v in response['task']['rewards']['items'][i].items():
                    text += f"  {k}: {v}\n"
            
        elif action in ('complete', 'exchange'):
            text = "--Rewards--\n"
            text += f"Gold: {response['rewards']['gold']}\n"
            for i in range(len(response['rewards']['items'])):
                for k, v in response['rewards']['items'][i].items():
                    text += f"{k}: {v}\n"                

        elif action == 'cancel':
            text += "Task canceled"

        data.append(text)
        answer['data'] = data
        cooldown = response['cooldown']['total_seconds']
        answer['cooldown'] = cooldown
        return answer

    def task_trade(self, info):
        # Task trade
        item = info['text']
        quantity =  info['quantity']
        answer, data, text = {}, [], ''
        payload = {'code': item, 'quantity': quantity}
        response = self._post('task/trade', payload=payload)
        if 'error' in response:
            return response
        response = response['data']
        self.char_info = response['character']

        data.append('--Items traded--')
        for k, v in response['trade'].items():
            text = f"{k}: {v}"
            data.append(text)
        answer['data'] = data
        cooldown = response['cooldown']['total_seconds']
        answer['cooldown'] = cooldown
        return answer

    
    def use_item(self, info):
        # Use item.
        item = info['text']
        quantity = info['quantity']
        answer, data, text = {}, [], ''
        payload = {"code": item, "quantity": quantity}
        response = self._post('use', payload=payload)
        if 'error' in response:
            return response
        else:
            response = response['data']
            self.char_info = response['character']
            
            data.append('--Item used--')
            data.append(f"Cooldown: {str(response['cooldown']['total_seconds'])}.")
            for key, value in response['item'].items():
                text = f"{key}: {value}"
                data.append(text)
            answer['data'] = data
            cooldown = response['cooldown']['total_seconds']
            answer['cooldown'] = cooldown
            return answer

    def recycling(self, info):
        item = info['text']
        quantity = info['quantity']
        answer, data, text = {}, [], ''
        payload = {"code": item, "quantity": quantity}
        response = self._post('recycling', payload=payload)
        if 'error' in response:
            return response
        else:
            response = response['data']
            self.char_info = response['character']
            
            data.append('--Item recycled--')
            data.append(f"Cooldown: {str(response['cooldown']['total_seconds'])}.")
            for i in range(len(response['details']['items'])):
                for key, value in response['details']['items'][i].items():
                    text = f"{key}: {value}"
                    data.append(text)
            answer['data'] = data
            cooldown = response['cooldown']['total_seconds']
            answer['cooldown'] = cooldown
            return answer
        
    def delete_item(self, info):
        # delete item
        item = info['text']
        quantity = info['quantity']
        answer, data, text = {}, [], ''
        payload = {"code": item, "quantity": quantity}
        response = self._post('delete', payload=payload)
        if 'error' in response:
            return response
        else:
            response = response['data']
            self.char_info = response['character']
            
            data.append('--Item deleted--')
            data.append(f"Cooldown: {str(response['cooldown']['total_seconds'])}.")
            for key, value in response['item'].items():
                text = f"{key}: {value}"
                data.append(text)
            answer['data'] = data
            cooldown = response['cooldown']['total_seconds']
            answer['cooldown'] = cooldown
            return answer
        
    def _deposit_withdraw(self, action, item, quantity, action_text):
        answer, data, text = {}, [], ''
        payload = {"code": item, "quantity": quantity}
        response = self._post(action, payload=payload)
        if 'error' in response:
            return response
        else:
            response = response['data']
            self.char_info = response['character']
            
            data.append(f'--Item {action_text}--')
            data.append(f"Cooldown: {str(response['cooldown']['total_seconds'])}.")
            for key, value in response['item'].items():
                text = f"{key}: {value}"
                data.append(text)
            answer['data'] = data
            cooldown = response['cooldown']['total_seconds']
            answer['cooldown'] = cooldown

            if action == 'bank/deposit':
                self.bank['items'] = response['bank'][:-1]
            else:
                self.bank['items'] = response['bank']
            with open(os.path.join(basedir, 'json', 'bank.json'), 'w') as f:
                f.write(json.dumps(self.bank, indent=2))
            return answer
        
    def deposit(self, info):
        # Deposit item into the bank
        item = info['text']
        quantity = info['quantity']
        return self._deposit_withdraw('bank/deposit', item, quantity, 'deposited')
        
    def withdraw(self, info):
        # Withdraw item from the bank
        item = info['text']
        quantity = info['quantity']
        return self._deposit_withdraw('bank/withdraw', item, quantity, 'withdrawed')

    def _deposit_withdraw_gold(self, action, quantity, action_text):
        answer, data, text = {}, [], ''
        payload = {"quantity": quantity}
        response = self._post(action, payload=payload)
        if 'error' in response:
            return response
        else:
            response = response['data']
            self.char_info = response['character']
            
            data.append(f'--Gold {action_text}--')
            data.append(f"Cooldown: {str(response['cooldown']['total_seconds'])}.")
            data.append(f"Quantity of gold: {response['bank']['quantity']}")           
            answer['data'] = data
            cooldown = response['cooldown']['total_seconds']
            answer['cooldown'] = cooldown

            self.bank['gold'] = response['bank']['quantity']
            with open(f'json_examples\\bank.json', 'w') as f:
                f.write(json.dumps(self.bank, indent=2))
            return answer

    def deposit_gold(self, info):
        quantity = info['quantity']
        return self._deposit_withdraw_gold('bank/deposit/gold', quantity, 'deposited')

    def withdraw_gold(self, info):
        quantity = info['quantity']
        return self._deposit_withdraw_gold('bank/withdraw/gold', quantity, 'withdrawed')
    
    def buy_bank_expansion(self, info):
        response = self._post('bank/buy_expansion')
        if 'error' in response:
            return response
        else:
            answer, data = {}, []
            response = response['data']
            self.char_info = response['character']
            
            data.append('--Bank expansion has bought--')
            data.append(f"Cooldown: {str(response['cooldown']['total_seconds'])}.")
            data.append(f"Price: {str(response['transaction']['price'])}")
            answer['data'] = data
            answer['cooldown'] = response['cooldown']['total_seconds']
            return answer

    def maps(self, info):
        answer, data = {}, []
        for i in range(len(self.maps_data)):
            if self.maps_data[i]['content']:
                text = f"Name: {self.maps_data[i]['name']}\n"
                text += f"Coordinates: x: {self.maps_data[i]['x']}, "
                text += f"y: {self.maps_data[i]['y']}\n"
                text += 'Content:\n'
                for k,v in self.maps_data[i]['content'].items():
                    text += f'  {k}: {v}\n'
                data.append(text)
        answer['data'] = data
        return answer

    def get_active_events(self, info):
        response = self._get('events/active')
        if 'error' in response:
            return response
        else:
            answer, data = {}, []
            response = response['data']

            data.append('--Active events--')
            for event in response:                
                data.append(f"Name: {event['name']}")
                data.append(f"X: {event['map']['x']}, Y: {event['map']['y']}")
                data.append(f"Duration: {event['duration']}")
                time_now = now = datetime.now(timezone.utc)
                expired_time = datetime.fromisoformat(event['expiration']).astimezone()
                data.append(f"Expiration: {str(expired_time)[:16]}")
                data.append(f"Created_at: {str(datetime.fromisoformat(event['created_at']).astimezone())[:16]}")
                data.append(f"Time left: {str(expired_time - time_now)[:4]}\n")
            answer['data'] = data
            return answer
        
    def npc_buy_sell_item(self, info):
        item = info['text']
        quantity = info['quantity']
        action = info['button_name'].lower().split()[0]
        payload = {'code': item, 'quantity': quantity}
        response = self._post(f"npc/{action}", payload=payload)
        if 'error' in response:
            return response
        else:
            answer, data = {}, []
            response = response['data']
            self.char_info = response['character']
            
            if action == 'buy':
                action = 'bought'
            else:
                action = 'sold'
            data.append(f'--Item {action}--')
            data.append(f"Cooldown: {str(response['cooldown']['total_seconds'])}.")
            for key, value in response['transaction'].items():
                data.append(f"{key}: {value}")
            answer['data'] = data
            answer['cooldown'] = response['cooldown']['total_seconds']
            return answer

    def get_npc_items(self, info):
        response = self._get(f"npcs/{self.npc_code}/items")
        if 'error' in response:
            return response
        else:
            answer, data = {}, []
            response = response['data']
            
            data.append(f'--{self.npc_code} has items for sell--\n')
            for item in response:
                for key, value in item.items():
                    data.append(f"{key}: {value}")
                data.append('')
            answer['data'] = data
            return answer
        
    def ge_buy_item(self, info):
        id = info['text']
        quantity = info['quantity']
        payload = {'id': id, 'quantity': quantity}
        response = self._post(f"grandexchange/buy", payload=payload)
        if 'error' in response:
            return response
        else:
            answer, data = {}, []
            response = response['data']
            self.char_info = response['character']
            
            data.append('--Item bought--')
            data.append(f"Cooldown: {str(response['cooldown']['total_seconds'])}.")
            for key, value in response['order'].items():
                data.append(f"{key}: {value}")
            answer['data'] = data
            answer['cooldown'] = response['cooldown']['total_seconds']
            return answer

    def ge_cancel_sell_order(self, info):
        id = info['text']
        payload = {'id': id}
        response = self._post("grandexchange/cancel", payload=payload)
        if 'error' in response:
            return response
        else:
            answer, data = {}, []
            response = response['data']
            self.char_info = response['character']
            
            data.append(f'--Order canceled--')
            data.append(f"Cooldown: {str(response['cooldown']['total_seconds'])}.")
            for key, value in response['order'].items():
                data.append(f"{key}: {value}")
            answer['data'] = data
            answer['cooldown'] = response['cooldown']['total_seconds']
            return answer
        
    def ge_create_sell_order(self, info):
        answer, data = {}, []
        if len(info['text'].split()) < 2:
            data.append('Text must contain item_code and price.')
            answer['data'] = data
            return answer
        item = info['text'].split()[0]
        price = info['text'].split()[1]
        quantity = info['quantity']
        payload = {'code': item, 'quantity': quantity, 'price': price}
        response = self._post("grandexchange/sell", payload=payload)
        if 'error' in response:
            return response
        else:
            response = response['data']
            self.char_info = response['character']
            
            data.append(f'--Sell order created--')
            data.append(f"Cooldown: {str(response['cooldown']['total_seconds'])}.")
            for key, value in response['order'].items():
                data.append(f"{key}: {value}")
            answer['data'] = data
            answer['cooldown'] = response['cooldown']['total_seconds']
            return answer

    def ge_get_sell_orders(self, info):
        answer = {}
        response = self._get('grandexchange/orders')
        if 'error' in response:
            return response
        else:
            data = []
            data.append('--Sell orders--')
            data.append(f"Total orders: {response['total']}.")
            data.append(f"Page number: {response['page']}")
            data.append(f"Orders on page: {response['size']}")
            data.append(f"Total pages: {response['pages']}\n")

            for order in response['data']:
                for k, v in order.items():
                    data.append(f"{k}: {v}")
                data.append('')

            answer['data'] = data
            return answer
        
    def ge_get_hystory(self, info):
        answer = {}
        response = self._get(f"grandexchange/history/{info['text']}")
        if 'error' in response:
            return response
        else:
            data = []
            data.append('--Sell item hystory for the last 7 days--')
            data.append(f"Total orders: {response['total']}.")
            data.append(f"Page number: {response['page']}")
            data.append(f"Orders on page: {response['size']}")
            data.append(f"Total pages: {response['pages']}\n")

            for order in response['data']:
                for k, v in order.items():
                    data.append(f"{k}: {v}")
                data.append('')

            answer['data'] = data
            return answer