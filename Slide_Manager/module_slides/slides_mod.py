from GoogleApiSupport import slides, auth
from GoogleApiSupport.auth import get_service_credentials_path, get_oauth_credentials_path
from Files_Handler.module.file_handler import Files_Handling

id_pres = "1rg1bvQHcgoJ571G7IkBJMynUpZeHROnWFP2JN3b25b4"
class Slides_Module(Files_Handling):
    def __init__(self, months_folder, presentation_id, cred_path):
        self.months_folder = months_folder
        super().__init__(months_folder)
        self.id_pres = presentation_id
        self.service_cred = get_service_credentials_path(cred_path)
        self.oauth_cred = get_oauth_credentials_path(cred_path)

data = slides.get_presentation_slides("1rg1bvQHcgoJ571G7IkBJMynUpZeHROnWFP2JN3b25b4")

month = Sheet_Manager("https://docs.google.com/spreadsheets/d/1yyCnFuKggnjTSx3mbp2eL8B8qSZY9SBdGH7k4Y1eQWY/")


x = read_json('slide_data.json')
page_id = []
for i in x:
   page_id.append(i["objectId"])
   

# months = month.month_and_last_month(1)
# month_current = months[1].upper()
# month_previous = months[0].upper()

# req_obj = [
#     {
#         "replaceAllText" :
#         {
#                 "replaceText": month_current, 
#                 "pageObjectIds": [page_id], 
#                 "containsText": {
#                                 "text" : "{MES_ATUAL}",
#                                 "matchCase" : True
#                             }
#         }
#     }
#         ]

# req_obj2 = [
#     {
#         "replaceAllText" :
#         {
#                 "replaceText": month_previous, 
#                 "pageObjectIds": [page_id], 
#                 "containsText": {
#                                 "text" : "{MES_ANTERIOR}",
#                                 "matchCase" : True
#                             }
#         }
#     },
#         ]


date_month = read_json('Janeiro.json')
# dates = []
# previous_month_id = []
# current_month_id = []
# for x in date_month:
#     if x['REDE'] == 'Instagram':
#         current_month_id.append(x["Janeiro"])
# print(date_month)

def get_info(json_obj, categoria, rede, subtype):
    for i in json_obj:
        if i["CATEGORIA"] == categoria and i['REDE'] == rede and i['SUBTIPO'] == subtype:
            return i
    return 'ERROR'

productions = {
    'cards' : get_info(date_month, 'Produções', 'Instagram', 'Formato: Card').get('Janeiro'),
    'videos' : get_info(date_month, 'Produções', 'Instagram', 'Formato: Vídeo').get('Janeiro'),
    'image' : get_info(date_month, 'Produções', 'Instagram', 'Formato: Imagem').get('Janeiro'),
    'stories' : get_info(date_month, 'Produções', 'Instagram', 'Formato: Stories').get('Janeiro')
}

req_production = [
    {
        "replaceAllText" :
        {
                "replaceText": str(productions['cards']), 
                "pageObjectIds": [page_id], 
                "containsText": {
                                "text" : "{cards_insta}",
                                "matchCase" : True
                            }
        }
    },

 {
        "replaceAllText" :
        {
                "replaceText": str(productions['videos']), 
                "pageObjectIds": [page_id], 
                "containsText": {
                                "text" : "{vid_insta}",
                                "matchCase" : True
                            }
        }
    },
{
        "replaceAllText" :
        {
                "replaceText": str(productions['image']), 
                "pageObjectIds": [page_id], 
                "containsText": {
                                "text" : "{img_insta}",
                                "matchCase" : True
                            }
        }
    },
{
        "replaceAllText" :
        {
                "replaceText": str(productions['stories']), 
                "pageObjectIds": [page_id], 
                "containsText": {
                                "text" : "{stor_insta}",
                                "matchCase" : True
                            }
        }
    },

    {
        "replaceAllText" :
        {
                "replaceText": str(productions['cards'] + 
                                   productions['videos']+ 
                                   productions['image'] + 
                                   productions['stories']), 
                "pageObjectIds": [page_id], 
                "containsText": {
                                "text" : "{sum_insta}",
                                "matchCase" : True
                            }
        }
    },
        ]
slides.execute_batch_update(req_production, id_pres)


# category_id = []
# subtype_id = []
# network_id = []
# previous_month_id = []
# current_month_id = []
# network_id
# for key in date_month:
#     category_id = key['CATEGORIA']
#     subtype_id = key['SUBTIPO']
#     network_id = key['REDE']
#     if subtype_id == 'Produções':
        


#    category_id.append(i["CATEGORIA"])
#    subtype_id.append(i['SUBTIPO'])
#    network_id.append(i['REDE'])
#    current_month_id.append(i['Janeiro'])
#    previous_month_id.append(i['Dezembro'])



   

# print(category_id)
# print(subtype_id)
# print(network_id)
# print(previous_month_id)
# print(current_month_id)

# if category_id == 'Número de Seguidores' and subtype_id == 'Total Geral' and network_id == 'Instagram':
#     print (category_id)
# else: 
#     print('nada')

# testes = [
#     {
#         "replaceAllText" :
#         {
#                 "replaceText": month_previous, 
#                 "pageObjectIds": [page_id], 
#                 "containsText": {
#                                 "text" : "{MES_ANTERIOR}",
#                                 "matchCase" : True
#                             }
#         }
#     }
#         ]
# slides.execute_batch_update(testes, id_pres)
# slides.execute_batch_update(req_obj, id_pres)

# write_json(data, 'slide_data.json')