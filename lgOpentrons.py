from error import UnAuthorizeException
import os
import requests
import json
import datetime
from datetime import datetime


class Labguru(object):

    def __init__(self, login, password, base='https://my.labguru.com'):
        data = {
            'login': login,
            'password': password,
            'base': base
        }

        url = base + '/api/v1/sessions.json'
        response = requests.post(url, data=data).json()
        if response.get('token') == '-1':
            raise UnAuthorizeException('Login failed! Wrong email or password')
        else:
            self.session = response

    def get_plates(self, id):
        """
        @Description: return list of plates from the experiment.
        @Param: the experiment id
        @Return list of plates or empty list if plates not found
        """

        plates_elements = requests.get(
            self.session.get('url') + 'api/v1/experiments/' + str(id) + '/elements.json?&element_type=plate',
            json={"token": self.session.get('token')}).json()


        plates = []
        for element in plates_elements:
            data = json.loads(element['data'])
            plates.append(data['wells'])

        return plates

    def get_samples(self, id):
        """
        @Description: return list of samples from the experiment.
        @Param: the experiment id
        @Return list of samples or empty list if samples not found
        """
        samples_elements = requests.get(
            self.session.get('url') + 'api/v1/experiments/' + str(id) + '/elements.json?&element_type=samples',
            json={"token": self.session.get('token')}).json()

        samples = []
        for element in samples_elements:
            data = json.loads(element['data'])
            samples.append(data['samples'])

        return samples


    def get_forms_data(self, id):
        """
        @Description: return list of forms data from the experiment.
        @Param: the experiment id
        @Return list of forms data or empty list if form not found
        """
        form_elements = requests.get(
            self.session.get('url') + 'api/v1/experiments/' + str(id) + '/elements.json?&element_type=form',
            json={"token": self.session.get('token')}).json()

        forms_data = []
        for element in form_elements:
            forms_data.append(json.loads(element['description'])['form_json'])

        return forms_data


    def add_step(self, id, txt):
        """
        @Description: add a new step to step element.
        @Param1: the experiment id
        @Param2: step text
        @Return api response
        """
        experiment = requests.get(
            self.session.get('url') + 'api/v1/experiments/' + str(id),
            json={"token": self.session.get('token')}).json()

        container_id = experiment['experiment_procedures'][-2]['experiment_procedure']['id']
        steps_element = requests.get(
            self.session.get('url') + 'api/v1/experiments/' + str(id) + '/elements.json?&element_type=steps',
            json={"token": self.session.get('token')}).json()

        step = [{
            "title": '<p>' + txt + '</p>',
            "timer": {
                "hours": "00",
                "minutes": "00",
                "seconds": "00"
            },
            "completed": True,
            "completed_by": "Robot",
            "completed_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }]

        if steps_element:
            steps = json.loads(steps_element[0]['data'])
            steps.append(step[0])
            response = requests.put(
                self.session.get('url') + 'api/v1/elements/' + str(steps_element[0]['id']) + '.json',
                json={"token": self.session.get('token'), "data": json.dumps(steps)})

        else:
            response = requests.post(self.session.get('url') + 'api/v1/elements.json',
                                     json={"token": self.session.get('token'),
                                           "item": {
                                               "container_id": container_id,
                                               "container_type": "ExperimentProcedure",
                                               "element_type": "steps",
                                               "data": json.dumps(step)}})

        return response

    def uploud_attachments(self, id, file):
        """
        @Description: uploud_attachments to the experiment.
        @Param1: the experiment id
        @Param2: file path
        @Return api response
        """
        with open(file, 'rb') as f:
            attachment = f.read()

        experiment = requests.get(
            self.session.get('url') + 'api/v1/experiments/' + str(id),
            json={"token": self.session.get('token')}).json()

        reponse = requests.post(
            self.session.get('url') + 'api/v1/attachments',
            data={
                'item[title]': os.path.basename(file),
                'item[attachable_type]': 'Knowledgebase::AbstractDocument',
                'item[attach_to_uuid]': experiment['uuid'],
                'token': self.session.get('token'),
            },
            files={'item[attachment]': (file, attachment)},
        )

        return reponse

    def update_stock_amount_used(self, id, stocks_id, amount_used, unit_type, unit_type_name):
        """
        @Description: update stock amount used.
        @Param1: the experiment id
        @Param2: stocks id
        @Param3: amount used
        @Param4: unit type
        @Param5: unit type name
        @Return api response
        """

        samples_elements = self.get_samples(id)
        for element in samples_elements:
            for sample in element:
                for stock in sample['stocks']:
                    if stock['id'] == stocks_id:
                        stock_sample = sample
                        print(stock_sample)

        return requests.post(
            self.session.get('url') + 'api/v1/stocks/' + str(stocks_id) + '/update_stock_amount.json',
            json={'token': self.session.get('token'),
                  'unit_type': unit_type,
                  'element_id': stock_sample['container']['id'],
                  'amount_used': str(amount_used),
                  'unit_type_name': unit_type_name,
                  'subtract': True,
                  'sample_id': stock_sample['id']}
        )