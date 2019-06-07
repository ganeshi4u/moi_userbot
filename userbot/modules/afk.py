# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.b (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module which contains afk-related commands """

import time

from telethon.events import StopPropagation
from userbot import (
    BOTLOG,
    BOTLOG_CHATID,
    CMD_HELP,
    COUNT_MSG,
    USERS,
    is_mongo_alive,
    is_redis_alive)
from userbot.events import register, errors_handler
from userbot.modules.dbhelper import is_afk, afk, afk_reason, no_afk

from telethon.tl.functions.contacts import BlockRequest
from telethon.tl.functions.users import GetFullUserRequest

@register(incoming=True, disable_edited=True)
@errors_handler
async def mention_afk(mention):
    """ This function takes care of notifying the
     people who mention you that you are AFK."""

    global COUNT_MSG
    global USERS
    if not is_redis_alive():
        return
    AFK = await is_afk()
    if mention.message.mentioned and not (await mention.get_sender()).bot:
        if AFK is True:
            if mention.sender_id not in USERS:
                await mention.reply(
                    "Sorry! I'm AFK due to ```" + await afk_reason() +
                    "```\nI'll get back to you once i'm online 😉."
		            "\n\n`This is an auto-generated reply by my bot`."
                )
                USERS.update({mention.sender_id: 1})
                COUNT_MSG = COUNT_MSG + 1
            elif mention.sender_id in USERS:
                if USERS[mention.sender_id] == 5:
                    await mention.reply(
                        "Sorry! But i'm still not yet available."
                        "\nStop spamming me."
                        "\nI'm busy with ```" + await afk_reason() +
			            "\n\n`This is an auto-generated reply by my bot`."
                    )
                    USERS[mention.sender_id] = USERS[mention.sender_id] + 1
                    COUNT_MSG = COUNT_MSG + 1
                elif USERS[mention.sender_id] == 10:
                    await mention.reply(
                        "This is my final warning!"
                        "\nSTOP or i'll block you."
			            "\n\n`This is an auto-generated reply by my bot`."
                    )
                    USERS[mention.sender_id] = USERS[mention.sender_id] + 1
                    COUNT_MSG = COUNT_MSG + 1
                elif USERS[mention.sender_id] >= 15:
                    await mention.reply(
                        "Alight that's it you're blocked!"
                        "\nHave a great day!"
			            "\n\n`This is an auto-generated reply by my bot`."
                    )
                    
                    """ Block the chat """
                    await mention.client(BlockRequest(mention.sender_id))
                    aname = await mention.client.get_entity(mention.sender_id)
                    name0 = str(aname.first_name)
                    uid = mention.sender_id

                    if not is_mongo_alive() or not is_redis_alive():
                        await mention.edit("`Database connections failing!`")
                        return

                    if BOTLOG:
                        await mention.client.send_message(
                            BOTLOG_CHATID,
                            "#BLOCKED\n"
                            + "User: " + f"[{name0}](tg://user?id={uid})",
                        )

                    USERS[mention.sender_id] = USERS[mention.sender_id] + 1
                    COUNT_MSG = COUNT_MSG + 1
                else:
                    USERS[mention.sender_id] = USERS[mention.sender_id] + 1
                    COUNT_MSG = COUNT_MSG + 1


@register(incoming=True)
@errors_handler
async def afk_on_pm(e):
    global USERS
    global COUNT_MSG
    if not is_redis_alive():
        return
    AFK = await is_afk()
    if e.is_private and not (await e.get_sender()).bot:
        if AFK is True:
            if e.sender_id not in USERS:
                await e.reply(
                    "Sorry! I'm AFK due to ```"
                    + await afk_reason()
                    + "```\nI'll get back to you once i'm online 😉."
		            "\n\n`This is an auto-generated reply by my bot`."
                )
                USERS.update({e.sender_id: 1})
                COUNT_MSG = COUNT_MSG + 1
            elif e.sender_id in USERS:
                if USERS[e.sender_id] % 5 == 0:
                    await e.reply(
                        "Sorry! But i'm still not yet available. "
                        "\nStop spamming me."
                        "\nI'm busy with ```"
                        + await afk_reason()
                        + "```"
			            "\n\n`This is an auto-generated reply by my bot`."
                    )
                    USERS[e.sender_id] = USERS[e.sender_id] + 1
                    COUNT_MSG = COUNT_MSG + 1
                elif USERS[e.sender_id] == 10:
                    await e.reply(
                        "This is my final warning!"
                        "\nSTOP or i'll block you."
			            "\n\n`This is an auto-generated reply by my bot`."
                    )
                    USERS[e.sender_id] = USERS[e.sender_id] + 1
                    COUNT_MSG = COUNT_MSG + 1
                elif USERS[e.sender_id] >= 15:
                    await e.reply(
                        "Alight that's it you're blocked!"
                        "\nHave a great day!"
			            "\n\n`This is an auto-generated reply by my bot`."
                    )
                    
                    """ Block the chat """
                    await e.client(BlockRequest(e.sender_id))
                    aname = await e.client.get_entity(e.sender_id)
                    name0 = str(aname.first_name)
                    uid = e.sender_id

                    if not is_mongo_alive() or not is_redis_alive():
                        await e.edit("`Database connections failing!`")
                        return

                    if BOTLOG:
                        await e.client.send_message(
                            BOTLOG_CHATID,
                            "#BLOCKED\n"
                            + "User: " + f"[{name0}](tg://user?id={uid})",
                        )

                    USERS[e.sender_id] = USERS[e.sender_id] + 1
                    COUNT_MSG = COUNT_MSG + 1
                else:
                    USERS[e.sender_id] = USERS[e.sender_id] + 1
                    COUNT_MSG = COUNT_MSG + 1


@register(outgoing=True, pattern="^.afk")
async def set_afk(e):
    if not e.text[0].isalpha() and e.text[0] not in ("/", "#", "@", "!"):
        if not is_redis_alive():
            await e.edit("`Database connections failing!`")
            return
        message = e.text
        try:
            AFKREASON = str(message[5:])
        except BaseException:
            AFKREASON = ''
        if not AFKREASON:
            AFKREASON = 'No reason'
        await e.edit("AFK AF!")
        if BOTLOG:
            await e.client.send_message(BOTLOG_CHATID, "You went AFK!")
        await afk(AFKREASON)
        raise StopPropagation


@register(outgoing=True)
@errors_handler
async def type_afk_is_not_true(e):
    global COUNT_MSG
    global USERS
    global AFKREASON
    if not is_redis_alive():
        return
    ISAFK = await is_afk()
    if ISAFK is True:
        await no_afk()
        x = await e.respond("I'm no longer AFK.")
        y = await e.respond(
            "`You recieved "
            + str(COUNT_MSG)
            + " messages while you were away. Check log for more details.`"
            + " `This auto-generated message "
            + "shall be self destructed in 2 seconds.`"
        )
        time.sleep(2)
        await x.delete()
        await y.delete()
        if BOTLOG:
            await e.client.send_message(
                BOTLOG_CHATID,
                "You've recieved " +
                str(COUNT_MSG) +
                " messages from " +
                str(len(USERS)) +
                " chats while you were away",
            )
            for i in USERS:
                name = await e.client.get_entity(i)
                name0 = str(name.first_name)
                await e.client.send_message(
                    BOTLOG_CHATID,
                    "[" +
                    name0 +
                    "](tg://user?id=" +
                    str(i) +
                    ")" +
                    " sent you " +
                    "`" +
                    str(USERS[i]) +
                    " messages`",
                )
        COUNT_MSG = 0
        USERS = {}
        AFKREASON = "No Reason"


CMD_HELP.update({
    "afk": ".afk <reason>(optional)\
\nUsage: Sets your status as AFK. Responds to anyone who tags/PM's \
you telling you are AFK. Switches off AFK when you type back anything.\
"
})
