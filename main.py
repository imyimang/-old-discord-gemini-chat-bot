import os
import re
import time
from datetime import datetime,timezone,timedelta
import aiohttp
import discord
import google.generativeai as genai
from discord.ext import commands
from dotenv import load_dotenv
import os.path

message_history = {}

dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
dt2 = dt1.astimezone(timezone(timedelta(hours=8)))

load_dotenv()

GOOGLE_AI_KEY = os.getenv("GOOGLE_AI_KEY")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
MAX_HISTORY = int(os.getenv("MAX_HISTORY"))

#---------------------------------------------AI Configuration-------------------------------------------------

# Configure the generative AI model
genai.configure(api_key=GOOGLE_AI_KEY)
text_generation_config = {
    "temperature": 0.6,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2000,
}
image_generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 2000,
}
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "block_none"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "block_none"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "block_none"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "block_none"}
]
text_model = genai.GenerativeModel(model_name="gemini-pro", generation_config=text_generation_config, safety_settings=safety_settings)
image_model = genai.GenerativeModel(model_name="gemini-pro-vision", generation_config=image_generation_config, safety_settings=safety_settings)


#---------------------------------------------Discord Code-------------------------------------------------
# Initialize Discord bot
bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

@bot.event
async def on_ready():
    print("----------------------------------------")
    print(f'Gemini Bot 已經登入 >>  {bot.user}')
    print("----------------------------------------")





#---------------------------------------------Message History-------------------------------------------------

def update_message_history(user_id, text):

    # Check if user_id already exists in the dictionary
    if user_id in message_history:
        # Append the new message to the user's message list
        message_history[user_id].append(text)
        # If there are more than 12 messages, remove the oldest one

        if len(message_history[user_id]) > MAX_HISTORY:

            path = os.path.abspath(f'{user_id}.txt')
            if os.path.exists(path):
            
                message_history[user_id] = []
                f = open(f'{user_id}.txt', "r", encoding="utf-8")
                f.seek(0)
                message_history[user_id].append(f.read())
            else:
                message_history[user_id].pop(0)





                
        
        # 將新的訊息寫入文件中

    else:
        # If the user_id does not exist, create a new entry with the message
        message_history[user_id] = [text]
        
        # 將新的訊息寫入文件中




def get_formatted_message_history(user_id):
    """
    Function to return the message history for a given user_id with two line breaks between each message.
    """
    if user_id in message_history:
        # Join the messages with two line breaks
        return '\n\n'.join(message_history[user_id])
    else:
        return "這位使用者並沒有任何歷史紀錄"

# On Message Function
@bot.event
async def on_message(message):
    
    if message.author == bot.user:
        return

    path = os.path.abspath(f'{message.author.id}.txt')
    if os.path.exists(path):
        with open(f'{message.author.id}.txt', "r", encoding="utf-8") as f:
            content = f.read()  # 讀取一次
            if content != "":
                msg = content
                update_message_history(message.author.id, msg)
 #   if str(message.author.id)   in message_history:        
  #      if len(message_history[message.author.id]) == MAX_HISTORY:
   #         update_message_history(message.author.id, str(f.read()))

    # Ignore messages sent by the bot

    


    # Check if the bot is mentioned or the message is a DM

    if isinstance(message.channel, discord.DMChannel):

        if str(message.content) == "查詢人設" or str(message.content) == "查看人設" or str(message.content) == "讀取人設":
            path = os.path.abspath(f'{message.author.id}.txt')
            if os.path.exists(path):
                with open(f'{message.author.id}.txt', "r", encoding="utf-8") as f:
                    f.seek(0)
                    content = f.read()
                    print(content)
                    
                    if content != "":
                        await message.channel.send(content)
                        f.close()
                    else:
                        await message.channel.send("並無儲存的人設")
                        f.close()
            else:
                await message.channel.send("並無儲存的人設")



        elif str(message.content) == "清空人設" or str(message.content) == "清除人設":
            f = open(f'{message.author.id}.txt', "w+", encoding="utf-8")
            f.write("")
            f.close()
            del message_history[message.author.id]
            await message.channel.send("人設已清空")



            

        else:
                f = open(f'{message.author.id}.txt', "w+", encoding="utf-8")
                f.write(message.content)
                f.close()

                await message.channel.send("人設已儲存")

    if isinstance(message.channel, discord.TextChannel):
            
            if str(message.channel.id) == "1189457765010251876":
                if message.author == bot.user:
                    return
     #   if bot.user.mentioned_in(message) :


                #Start Typing to seem like something happened
                cleaned_text = clean_discord_message(message.content)


            



                f = open('ai_log.txt', "a", encoding="utf-8")
                mt = dt2.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f'{mt}\n{str(message.author)}({str(message.author.id)})\n在 "{str(message.guild.name)}"({str(message.guild.id)})提問了:\n\n {cleaned_text} \n\n')

                async with message.channel.typing():
                    # Check for image attachments
                    if message.attachments:
                        print("有一則新訊息來自:" + str(message.author.name) + "(" + str(message.author.id) + ")" + ": " + cleaned_text)
                        #Currently no chat history for images
                        for attachment in message.attachments:
                            #these are the only image extentions it currently accepts
                            if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                                await message.add_reaction('🎨')

                                async with aiohttp.ClientSession() as session:
                                    async with session.get(attachment.url) as resp:
                                        if resp.status != 200:
                                            await message.channel.send('圖片載入失敗')
                                            return
                                        image_data = await resp.read()
                                        response_text = await generate_response_with_image_and_text(image_data, cleaned_text)
                                        #Split the Message so discord does not get upset
                                        await split_and_send_messages(message, response_text, 1700)
                                        return
                    #Not an Image do text response
                    else:
                        print("有一則新訊息來自:" + str(message.author.id) + ": " + cleaned_text)
                        #Check for Keyword Reset

                            #End back message
                        if "RESET" in cleaned_text or "reset" in cleaned_text or "Reset" in cleaned_text:
                        #    if bool(888098958663102485 in message_history) == False:
                         #       await message.channel.send("nelson bot沒有短期記憶")
                         #   if 888098958663102485 in message_history:
                          #      message_history[888098958663102485] = ""
                           #     await message.channel.send("歷史紀錄已重製")

                            if message.author.id in message_history:
                                del message_history[message.author.id]
                                await message.channel.send("🤖 歷史紀錄已被 " + str(message.author.name) + " 重置")
                                print("🤖 歷史紀錄已被 " + str(message.author.name) + " 重置")
                                return
                        await message.add_reaction('💬')

                    
							    
							    
							    
							    
                                
                        #Check if history is disabled just send response
                        if(MAX_HISTORY == 0):
                            response_text = await generate_response_with_text(cleaned_text)
                            #add AI response to history
                            await split_and_send_messages(message, response_text, 1700)
                            return;
                        #Add users question to history
                        update_message_history(message.author.id,cleaned_text)
                        response_text = await generate_response_with_text(get_formatted_message_history(message.author.id))
                        #add AI response to history
                        update_message_history(message.author.id,response_text)
                        #Split the Message so discord does not get upset
                        await split_and_send_messages(message, response_text, 1700)



            else:
                if bot.user.mentioned_in(message) :
                    #Start Typing to seem like something happened
                    cleaned_text = clean_discord_message(message.content)


                



                    f = open('ai_log.txt', "a", encoding="utf-8")
                    mt = dt2.strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f'{mt}\n{str(message.author)}({str(message.author.id)})\n在 "{str(message.guild.name)}"({str(message.guild.id)})提問了:\n\n {cleaned_text} \n\n')

                    async with message.channel.typing():
                        # Check for image attachments
                        if message.attachments:
                            print("有一則新訊息來自:" + str(message.author.name) + "(" + str(message.author.id) + ")" + ": " + cleaned_text)
                            #Currently no chat history for images
                            for attachment in message.attachments:
                                #these are the only image extentions it currently accepts
                                if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                                    await message.add_reaction('🎨')

                                    async with aiohttp.ClientSession() as session:
                                        async with session.get(attachment.url) as resp:
                                            if resp.status != 200:
                                                await message.channel.send('圖片載入失敗')
                                                return
                                            image_data = await resp.read()
                                            response_text = await generate_response_with_image_and_text(image_data, cleaned_text)
                                            #Split the Message so discord does not get upset
                                            await split_and_send_messages(message, response_text, 1700)
                                            return
                        #Not an Image do text response
                        else:
                            print("有一則新訊息來自:" + str(message.author.id) + ": " + cleaned_text)
                            #Check for Keyword Reset
                            if "RESET" in cleaned_text or "reset" in cleaned_text or "Reset" in cleaned_text  :
                                #End back message
                                if message.author.id in message_history:
                                    del message_history[message.author.id]
                                await message.channel.send("🤖 歷史紀錄已被 " + str(message.author.name) + "重置")
                                print("🤖 歷史紀錄已被 " + str(message.author.name) + "重置")
                                return
                            await message.add_reaction('💬')

                            #Check if history is disabled just send response
                            if(MAX_HISTORY == 0):
                                response_text = await generate_response_with_text(cleaned_text)
                                #add AI response to history
                                await split_and_send_messages(message, response_text, 1700)
                                return;
                            #Add users question to history
                            update_message_history(message.author.id,cleaned_text)
                            response_text = await generate_response_with_text(get_formatted_message_history(message.author.id))
                            #add AI response to history
                            update_message_history(message.author.id,response_text)
                            #Split the Message so discord does not get upset
                            await split_and_send_messages(message, response_text, 1700)

#---------------------------------------------AI Generation History-------------------------------------------------

async def generate_response_with_text(message_text):
    prompt_parts = [message_text]
    print("提問: " + message_text)
    response = text_model.generate_content(prompt_parts)
    if(response._error):
        return "❌發生錯誤" + "錯誤代碼如下\n" + "```\n" + str(response._error) + "\n```"
    return response.text

async def generate_response_with_image_and_text(image_data, text):
    image_parts = [{"mime_type": "image/jpeg", "data": image_data}]
    prompt_parts = [image_parts[0], f"\n{text if text else '這張圖片代表什麼?'}"]
    response = image_model.generate_content(prompt_parts)
    if(response._error):
        return "❌發生錯誤" + "錯誤代碼如下\n" + "```\n" + str(response._error) + "\n```"
    return response.text



#---------------------------------------------Sending Messages-------------------------------------------------
async def split_and_send_messages(message_system, text, max_length):

    # Split the string into parts
    messages = []
    for i in range(0, len(text), max_length):
        sub_message = text[i:i+max_length]
        messages.append(sub_message)

    # Send each part as a separate message
    for string in messages:
        await message_system.channel.send(string)

def clean_discord_message(input_string):
    # Create a regular expression pattern to match text between < and >
    bracket_pattern = re.compile(r'<[^>]+>')
    # Replace text between brackets with an empty string
    cleaned_content = bracket_pattern.sub('', input_string)
    return cleaned_content






#---------------------------------------------Run Bot-------------------------------------------------
bot.run(DISCORD_BOT_TOKEN)
