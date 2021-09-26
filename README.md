# Alune-Discord-Bot
![Alune](https://github.com/jaymay284/Alune-Discord-Bot/blob/main/Alune.jpg?raw=true)
## Discord bot written in Python 3.0

##Database:
- Alune Bot will log user events in the server, uses UserID, GuildID, UserName, and DateLastActive (per server) and can create embeds that display general server activity.
- Alunebot can use `!checkActivity` and `!checkInactivity {date}` to determine which users are most-recently active and which users have been __inactive__ for whatever amount of time.

## checkActivity:
Shows a recent summary of the most recent user activity in the guild.
- Takes no parameters

## checkInactivity: 
Shows a summary of users who have been inactive since the input date.
- Takes text-date parameter, is in the form `YYYY/MM/DD`
- E.x. `!checkInactivity 2021/9/25` will show which users have been inactive since before Sept. 25, 2021.
