import opentrons.execute
import requests
import json
import import_ipynb
import csv
import labguru

experiment_id = 512
plate = labguru.get_plate(experiment_id)
samples = labguru.get_samples(experiment_id)
data = labguru.get_form_data(experiment_id)

protocol = opentrons.execute.get_protocol_api('2.8')
protocol.home()

plate1 = protocol.load_labware(data['source_plate'], 4)
plate2 = protocol.load_labware(data['destination_plate'], 7)
tiprack_1 = protocol.load_labware('opentrons_96_tiprack_300ul', 10)
p50_multi = protocol.load_instrument('p50_multi', 'right', tip_racks=[tiprack_1])


counter = 0
for sample_index in range(len(samples)):
    p50_multi.pick_up_tip()
    p50_multi.aspirate(data['transfer_volume'], plate1.rows()[0][sample_index])
    for stock_index in range(len(samples[sample_index]['stocks'])):
        p50_multi.dispense(10, plate2.rows()[0][counter])
        counter +=1
    p50_multi.drop_tip()

with open('Cell culture - Assay Preparation.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['id', 'coordinates', 'samples', 'stock', 'concentration'])
    for cell in plate:
        writer.writerow([cell['id'], cell['coordinates'], cell['samples'][0],
                         cell['samples_metadata'][str(cell['samples'][0])]['stocks'],
                         cell['samples_metadata'][str(cell['samples'][0])]['concentration']])
        labguru.update_stock(cell, experiment_id, data['transfer_volume'])

labguru.uploud_attachments(file, experiment_id)
labguru.add_steps(experiment_id)

protocol.home()
for line in protocol.commands():
    print(line)