import lgOpentrons

id = 655  # new experiment
file = r'xxxxxxxxxxxxxxxxxxxxxxxxx'
# id = 651

lab = lgOpentrons.Labguru(login="xxxxxxxxxxxx", password="xxxxxxxxxxxxxxxxxx")
print(lab.get_plates(id))
print(lab.get_samples(id))
print(lab.get_forms_data(id))
print(lab.add_step(id, 'hi'))
print(lab.uploud_attachments(id, file))
print(lab.update_stock_amount_used(id, stocks_id=251, amount_used=1, unit_type='volume', unit_type_name='mL'))
