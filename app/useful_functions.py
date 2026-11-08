from datetime import datetime as dt
async def get_choice_from_name(name):
    name=str(name)
    return name[:name.find('|')]

async def data_extension(data,message,object_name,anti_extension):
    if anti_extension:
        lst = data.get(object_name, [])
        lst.remove(message)
    else:
        lst = data.get(object_name, [])
        lst.append(message)
    return lst

async def calculate_time_zone_difference(user_hour):
    server_hour = dt.now().hour
    user_hour=int(user_hour)
    return str(user_hour-server_hour)