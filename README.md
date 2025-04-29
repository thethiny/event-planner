### Plan

.Login users manually, 
Group has members (ex, 1,2,3,4) want to be able to choose a member and see his attendance history and his attendance summary, (ex, missed an important meeting, so) once meeting is done, want to be able to write a summary to everyone in that invitation list, and they will receive an email( this is what was discussed in time slot 1 and 2) end of every week or once final timing I’d done, we’re gonna send a different type of summary (ex, this week these people went to this meeting and people missed “this” meeting”).

Events with slots with different times EX. People attend 6am others attend 4pm, monthly server sync ups

Goal: create an event with a slot and require (specific people/ opt) to join that event, the an email will be sent to those people, once the open it the will be able to choose what event to join and the time will be converted into their time zone.

Extra: we want to be able to create an extra endpoint for extra stuff, that will take your events and display it in your counter 


eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImV4YW1wbGVfdXNlciIsInRva2VuX2lkIjoiZWZiMzM4ODI4YjBmNGQifQ.6J51M0EIz9EcECZ7YRkxy1oYahBPcKtL1VyPHGN4chk
extra stuff:
1- /calendar -> create an .ics calendar for your user to sync with Outlook/Google Calendar
2- Email API -> SendInBlue
3- Login -> Customized JWT Tokens
4- Utilities -> MongoDB Atlas, SendInBlue, Workers: Koyeb, Deployment: Github Actions connected with Oracle Cloud VM

# REF
https://chatgpt.com/share/68102d01-6970-8006-a080-654a510b1024