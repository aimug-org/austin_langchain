### Key Points
**Key Points**  

[📝 **Austin LangChain Users Group - AIMUG Community Call Notes**](https://app.krisp.ai/n/Austin-LangChain-Users-Group---AIMUG-Community-Call--6213476b247f4a31a51a977baf6feb57?nopreview)

🕞 Started at 02:04 PM on 26 Sep, lasted 52m

  

- Colin provided an update on the Hacky Hour review, discussing the venue, participation, and communication.
- The group discussed plans for the upcoming showcase event, including the layout, AV setup, and providing snacks.
- Colin shared updates on the Docky Source project, including the creation of a documentation site using Claude Dev.
- Saurabh introduced the new Google Model called Data JAMA and its concept of Retrieval-Augmented Generation (RAG).
- Saurabh demonstrated a LinkedIn post automation tool he built for generating social media content.
- Karim proposed exploring the use of Anthropic's Constitutional AI (ConstitutionalAI) and its potential integration with LangChain.
- The group discussed the idea of building a tool generation concept using LangChain and other AI tools.

### Actions

**Action Items**  

[📝 **Austin LangChain Users Group - AIMUG Community Call Notes**](https://app.krisp.ai/n/Austin-LangChain-Users-Group---AIMUG-Community-Call--6213476b247f4a31a51a977baf6feb57?nopreview)

🕞 Started at 02:04 PM on 26 Sep, lasted 52m

  

- Colin to follow up with Brian and Tamara for a dry run of the AV setup, potentially on Monday or Tuesday. - Colin
- Colin to conduct AV testing at the venue to ensure remote audio input works and can be output through the system. - Colin
- Rob to assist with on-site or remote testing of the AV system, focusing on hooking up equipment and testing microphones. - Rob
- Karim to assist with AV testing at the venue. - Karim
- Colin to work with Brian on room layout, planning to set up circular round-top tables for the event. - Colin
- Colin to purchase snacks and drinks from Costco for the event on Tuesday night. - Colin
- Ricky to prepare the intro session/presentation for the October 2nd event. - Ricky
- Saurabh to clean up and share the LinkedIn post agent notebook, removing personal access tokens. - Saurabh
- Saurabh to share the LinkedIn post automation tool notebook during next week's office hours or community call. - Saurabh
- Karim to explore DSPY and compare its strengths with LangChain. - Karim
- Colin to post the transcript of this meeting to GitHub under meeting transcripts. - Colin
- Karim to run the meeting transcript through notebook element once it's posted. - Karim
### Outline
**Outline**  

[📝 **Austin LangChain Users Group - AIMUG Community Call Notes**](https://app.krisp.ai/n/Austin-LangChain-Users-Group---AIMUG-Community-Call--6213476b247f4a31a51a977baf6feb57?nopreview)

🕞 Started at 02:04 PM on 26 Sep, lasted 52m

  

**Hacky Hour Event Review**

- The recent Hacky Hour event was held at a venue on the East Side of Austin, which received positive feedback for its ease of access and ample parking.
    
- Participants appreciated having the venue to themselves, allowing for better networking opportunities and project sharing.
- Access to Claude Dev during the event enabled real-time exploration of its limitations.
- There was discussion about using the venue's large TV for future events, possibly for screencasting, while agreeing to be respectful of the establishment.
- Colin suggested scheduling the next Hacky Hour at the same location before considering new venues.
    

  

**Upcoming Showcase Event Planning**

- Plans for an upcoming showcase event at the Center for Civil Government were discussed, including a dry run scheduled for Monday or Tuesday to test the AV system and ensure smooth remote audio integration.
    
- The venue features three screens: a large central screen and two smaller side screens.
- A conference-style layout with round tables was proposed by Colin to accommodate laptops and facilitate group discussions.
- The event will include a mixer, presentations, and a panel discussion.
- New attendees may be clustered in one area of the room to provide focused support and integration.
- Light refreshments will be provided, with Colin offering to purchase snacks and drinks from Costco.
- Current registration stands at 25 people, with expectations of reaching 50 attendees by the event date.
    

  

**Docusaurus Project Updates**

- Colin presented updates on the Docusaurus project, accessible at amug.org, highlighting key features such as a root site with direct links to introduction, high-level bullet points, and links to Discord, Meetup, YouTube, Twitter, and GitHub.
    
- An enabled blog module is pending content.
- The events section has been updated using Claude Dev to generate content from their Meetup page.
- A comprehensive archive of past notebooks and presentations is organized by month.
- The website aims to showcase the group's early adoption and innovation in the AI space.
    

  

**Open Forum Discussions**

- Saurabh shared information about Google's new Data GMMA model, introducing the concept of Retrieval Interlevel Generation (RIG), and provided links to research papers and Google Colab notebooks for further exploration.
    
- Saurabh demonstrated a LinkedIn post agent capable of generating entire posts, including data scraping and thumbnail creation, discussing its potential use for automating content creation for social media presence.
- Karim mentioned plans to explore DSPY to understand its strengths and potential integration with Langchain.
- The idea of developing a content distribution pipeline that could generate material from existing conversations and meetings was briefly touched upon.
- Karim discussed plans to work on a tool generation concept, potentially using React Agent and LangGraph to create a system that can dynamically generate tools based on user requirements.
    

  

**Meeting Conclusion**

- Participants expressed enthusiasm for the various projects discussed and agreed to continue collaborative efforts in exploring and developing AI-driven tools and applications.

### Transcript

**Colin McNamara | 00:18  
**Where am I? Can everyone hear? Mem?  
**Rob | 00:30  
**I got you. Can you hear me?  
**Colin McNamara | 00:31  
**Yeah im clear cool.  
**Rob | 00:34  
**Cool. I'm in a mute 'cause I'm having a late lunch. But.  
**Colin McNamara | 00:39  
**Apparently the sessions is it's just that link I got into a new link let me post a new link here so we can it doesn't matter actually, it doesn't matter anyways. Yeah, this work. Okay. Let's give a few more minutes for everyone to log on and we can get started.  
**Ryan | 01:07  
**Want to see your first shirt test?  
**Colin McNamara | 01:09  
**Yeah.  
**Ryan | 01:14  
**DRW on one that if it didn't work, then it's fine to throw away, but they came out pretty good.  
**Colin McNamara | 01:25  
**Where am I looking for in off topic? No, okay, in this room. Let see magic happening here.  
**Ryan | 01:51  
**There we go.  
**Colin McNamara | 01:52  
**Okay, what? Okay, that's sick.  
**Ryan | 01:56  
**I'm not the biggest fan of this one. I'm gonna have to clean it up because it chops off the play chain at the top, but it still looks good.  
**Colin McNamara | 02:03  
**Yeah.  
**Ryan | 02:07  
**But I think this logo looks better.  
**Colin McNamara | 02:13  
**Wow, okay, that's cool. Can I change my logo request or is it too late?  
**Ryan | 02:19  
**Yeah, I don't think the only problem with this one is in this lower corner down here, the AI, instead of saying welcome to Austin or welcome to Texas.  
**Colin McNamara | 02:30  
**Yeah, that that's rad, absolutely switch to that for me, that's pretty cool.  
**Ryan | 02:31  
**It kind of blended Texas and Austin together, so I got to clean that up, but I think it still looks pretty sick.  
**Karim Lalani | 02:48  
**Yeah.  
**Ryan | 02:50  
**That was pretty simple. I might need to give up my tech career and start building t shirts.  
**Colin McNamara | 02:53  
**[Laughter] You know, you could have an empire.  
**Saurabh | 03:00  
**Y.  
**Colin McNamara | 03:01  
**That's really cool, I really appreciate you doing that. That's cool.  
**Ryan | 03:05  
**Absolutely. Yeah, it was.  
**Saurabh | 03:09  
**It's cool.  
**Colin McNamara | 03:10  
**Cool. Okay, well, seven o'clock. It's a seven past hour. Whoever's going to join, you're gon to join. Post Topics 02:26 Hacky Hour Review 32 Event Planning for the showcase. I want to give you a quick update on what we've been able to move forward with Dokysaurus and then open form. Are there any other topics that people would like to discuss? Okay, let's kick it off. 2:26 Hacky hour review. Do we have any feedback? And Rob was there.  
And robs eating.  
**Rob | 03:53  
**Very well. Well, while I eat. That was good. I mean, I just enjoy networktorking with you guys, hearing what people are doing.  
**Colin McNamara | 03:59  
**Yeah, cool. Anything that can be improvedmm.  
**Rob | 04:12  
**No, I mean, I like that you're finding these off the beaten paths, at least for me. East Austin stuff. You know, it was easy to get to, parking was fine. And, I thought the venue. It kind of felt like we had the venue to ourselves in a way. I know there's a couple of other people over on side, but I thought that was a good setup for.  
**Colin McNamara | 04:29  
**Nice. Cool. I think this our second or third time there, I think third.  
**Rob | 04:39  
**To that location. I don't think I've been to that location yet, so I must have just skipped.  
**Colin McNamara | 04:42  
**Okay, I okay, yeah, awesome, I like it too.  
**Rob | 04:45  
**I've only been in a couple of hacky hours anyway. But. But like it.  
**Colin McNamara | 04:53  
**It's kind of unique to the East Side. I think they're gonna be doing a lot of upgrades in that area, so we only have so long to enjoy those bars before they turn into lash bars and nail salons. Let me see. Cool.  
Yeah, I thought. I thought it worked out. We pretty much had to had the wrong place. They moved the two dollar pint special from Wednesday to Thursday, which was a slight bummer, but, other than that, it seemed like everyone had a good time. New people came in where? We'll spend time with them. Get them integrated. I liked, that had a Claude dev open and running it while interacting and saw like the limitations of that. Let me see, that's my feedback. I'm asking. We're going through our proposed topics today. Or the 02:26 hour review three two event planning am mug duck source updates and then open form. Is there anything you want to add to the.  
**Vaskin | 05:54  
**No, I.  
**Colin McNamara | 05:55  
**Okay, so we're we'res at towards the end of the Hacky review. What are your thoughts of the Hacky venue participation? Being able to communicate, whatever.  
**Vaskin | 06:12  
**Are you asking me? Yeah, I thought it was fine, like, no, I thought it was good.  
**Karim Lalani | 06:17  
**I wasn't sure.  
**Vaskin | 06:19  
**How much WiFi they had, and I didn't know that. You know, I didn't even get my laptop. Just have you, done. You're doing a good job.  
**Colin McNamara | 06:32  
**Yeah.  
**Vaskin | 06:32  
**And I hadn't used the web feature yet, so that was the first I saw it.  
**Colin McNamara | 06:38  
**Awesome.  
Yeah, I liked how we had a new person come in and talk to me for a little bit and this guy Mike. And it was really nice to be able to, like, have a conversation and then hand off when Cream was going through his kind of a deskboard they had made. It's nice to be able to talk about concepts and then drive drop right and drop right into like a learning the open moment. So.  
**Rob | 07:03  
**If we're the if we're contin to be the only ones there, we ought to just screencast to one of those T. Vs. And like, say, okay, it's with old bar.  
**Colin McNamara | 07:11  
**Maybe. Maybe. And the back patios open too.  
So we're kind of getting in that weather. We can start enjoying the patios and they have a g enormous TV something to think about. Maybe I'll talk to see and talk to bar owners.  
**Rob | 07:25  
**Well, yeah, I'm kind of half joking.  
I mean, as nice as it would be, I'd.  
**Colin McNamara | 07:28  
**Yeah, I take it over.  
**Rob | 07:30  
**I don't want to like, you know.  
I mean, if they're. If theyre cool with it, you know, i guess that'd be cool.  
**Vaskin | 07:36  
**And I don't take it over.  
**Colin McNamara | 07:36  
**I know, yeah, that would be fun.  
**Vaskin | 07:38  
**I think we should just project max headroom onto every one of those.  
**Karim Lalani | 07:41  
**T80 [Laughter].  
**Colin McNamara | 07:44  
**I have portable projectors and battery packs, too. There's a lot of like kind of a newground stuff that we can play with if we want to.  
Yeah. No, it'sine. I'm. I'm leaning towards scheduling the next one to the same location and then probably find another place we can explore past then. Yeah. So keep exploring the East side and other areas. East Side, central and other areas around here. What's everyone's thoughts on that?  
Okay, hey Graham, you saw the proposed some of the confusion sessions have an issue. Let me see you saw the proposed schedule or proposed agenda we're at the we're finishing up with Hacky review capture. Any feedback from you regarding Hacky? What went well, what could be improved thoughts?  
**Karim Lalani | 08:50  
**Hacking or was great. I think, had a lot of discussion around, you know, almost the stuff that we want to. We'll probably be covering in the panel discussions about, you know, what works, what doesn't work.  
Well, at least in, you know, in discussions that where I was involved, what worked for me, what didn't work for me, how I would use it and where I would avoid it.  
**Colin McNamara | 09:14  
**Yep. Awesome.  
Yeah, I felt that too. I was like, okay, this is kind of nice to see get a little warm up for any of the questions I might be asking and the topics might be going over, as well as kind of my own personal experience to be able to throw some color in there.  
**Rob | 09:27  
**Incidentally, I tried to throw a big old task at Claude Dev last night and kind of threw up all over my repo. So I just thought I got. I got sick of like I was architecting it myself, and like, you know what? I'm just gonna see how far this thing can run with something. And it didn't work. It didn't end so well, but it. It was kindly able to, reverse course and get it back. Get the repo back to where it was pretty easily.  
So that's a good thing about it.  
**Colin McNamara | 09:54  
**That's really cool.  
Yeah, I've been having a lot of fun. I definitely want to loop back to the part of my Doctor Source Update story, which was the project that I was like, okay. And that's why I'm going to hack on one here. And, you know, came up with some really fun stuff. I definitely do see the value of code based contacts. Be able to pass in structured information that sits in the beginning of the. That sits actively in the beginning of the window, to be able to manage topics falling and falling off that first and first out queue. Okay, any other things we need to discuss about Hacky? No. Okay.  
And then. Just I suggested scheduling the one at Skinny's again. And then we'll figure out you know what? And we'll figure out in the cycle, like where's another place around town, ideal on the East Side or central that we can explore and continue to fun stuff fun people in the world learning. Okay, through two event planning.  
So we have a showcase, a mixer showcase with full access to the full room at the Center for Civil Government. Civil Civic Service. I need to follow up with Brian and Tamara for a dry run one. Maybe Monday, maybe Tuesday, depending on my schedule. Looks, my accountant is yelling at me for some stuff that I need to get done before in October first, so that is going to take priority for a little bit, but, let me see.  
So for three two event planning, we had Jackson Cam have a email rag Samwise, we had, your Perplexity clone, and then we had a panel. I'd see there's a couple things we need to figure out, and that's really getting out there. Monday or Tuesday for a B test is in the with the AV system there like how do we pipe it through while using the h my switchers and I should be able to dedicate some time on Monday for that.  
So that'll be kind of a go no go on a couple of things. The one thing that I've seen work before in that, for government form, that was in the open government forum with microphones do work and loops in and out. And you know, we distributed some microments throughout the room last time with Cam, and so we pulled that. There is nothing I still owe an action of adding everyone to the dscript project so everyone can edit the stuff.  
So throw that out there and let me see. So for three two event planning, Rob and you volunteered to help out either remotely or pop in. I think he did too, for whenever I get out there for the dry run and I see.  
**Rob | 12:56  
**Yes, I'm on to that.  
**Colin McNamara | 12:57  
**Okay, cool. I appreciate that. And Sora. Hopefully that'll allow us to provide a smooth road for you and your. Your connection, does that sound good?  
**Saurabh | 13:13  
**I woke up very early that day. I mean, I it is a bit disheartening not to be able to present, but, yeah, I'm. I'm happy to do it whenever I can.  
**Colin McNamara | 13:25  
**Okay, cool, so we'll give you a heads up on, like, Monday or whether we're able to fix the techical issues new site, new rooms, new gear.  
So, you know, we're learning here. I appreciate your flexibility.  
**Saurabh | 13:36  
**No worries.  
**Colin McNamara | 13:37  
**Waking up early, you know. Did her best in the time. Let me see what else we need to do for three, two event pointing. Let's actually see how many people are signed up, which we'll have to track because usually the majority of people sign up that week.  
So let's go to Austin Lane Chain unlocking AI with Lane Chain, we have 25 people signed up. So I'm guessing only like 30 or 40, by signed up by the time by next week, usually about doubles, so I know 50 or so. I'll work with Brian to get a layout. I'm thinking about doing more of a conference layout where there is put a circle tables like eight tops or ten tops, whatever they are, so we can put those out there and if we need to scale, we can bring in extra chairs that allow us to have people with their laptops out. One thing is AV test and one traut. There's three screens. There's like a giant screen in the center and two, two two screens on the side. And Ricky said he would do the one the full one on one, right?  
So the PowerPoint overview in the lab. I want to see if I can get him set up on one screen to start with. Now to kind of cluster the new people either to the right or the left side.  
And then we can have, like the mixer going over to the rest of it. So they'll put allow us to have like a cluster of people new that we can have one one of our core members at the table with them, right to help out.  
And then. Then as we go into the main event and bring up the main. Bring up the main screen.  
So bunch a B stuff. Let me see. What are other ideas that, I'm want to throw a little bit of cash down for, like, some snacks. I was thinking some, like, trays from Costco or something like that. Does anyone have any thoughts on that?  
So we can have some sodos and light snacks as well as tables there.  
**Karim Lalani | 15:50  
**Yup. Sounds like a plan. I'm happy to pitch in as well.  
**Colin McNamara | 15:54  
**That's awesome. I appreciate that. If there's any chance anyone can s the best situation is someone is able to, like, drive by if they if their commute passes by. Costco is able to pick some bring some stuff or pick something up on the way in. I can like I can reimburse on receipt if needed. Or I can just go up on Tuesday. Tuesday night and pick something up from Costco. Either way we will.  
**Karim Lalani | 16:25  
**Yeah, I'll be driving straight from work, so I don't believe there's a Costco in that area. Plus, I don't have. I'm not on the membership either.  
**Rob | 16:32  
**So I've got a Costco membership, and I'm not that far from one. I'm just a little hesitant because, I don't know my schedule for that day very well yet. Actually, I do, and it doesn't look good. I've got my daughter's ortho appointment, which is kind of up north, so.  
**Colin McNamara | 16:49  
**Okay, that's okay.  
**Rob | 16:50  
**Sorry, I should looked at my calendar before I opened my mouth, but. But ordinarily, yeah, maybe for another event.  
You know, pencil me in. Because I'm. I'm not that far from Costco from coming from home.  
**Colin McNamara | 17:01  
**Cool.  
So I'll drive up Tuesday night or whenever cost goes open and pick up some trays the c it works out. Sorry if anyone wants crappy food. But it. It's probably gonna be vegetables. And like those little Pinll Pino rolls and stuff, but, you know, got avoid the dies. Let me see, and I'll do the same thing. Non alcoholic. I still have like half the soda, half the drinks I brought in the last time I still have.  
So bring that in. Is there anything else that any ideas people want to cover for our three two in person of it? Cool. For panel members, keep this. Really? I don't know. I want to basically have like, maximum impact, minimum effort, and a good opportunity for mingling and connecting with each other. Okay, I see. I'll switch over to the next item, which is Docky source updates. Not done yet, but if you go to amu dot org we have the start of basically a document site. And let me see how the heck do I share my Desk share an application here screen Share welcome go Live. Okay. Cool.  
So. I. With little help from Baskin set up like the base repo for docky source and give me walk through the documentation where certain files were. And that's been really cool. Took that and point ar anator at it. Excuse me, Claude Deb at it and made some updates so you can go this on your phone. It works. You can go to here.  
So one of the main things I notice, and we're trying to bring people on board, people on, is that, you know, we're like, okay, go to threepo, let's GitHub this type of stuff. So created the root site, which has direct links to our introduction. High level bullet points about what we do at the bottom links to our Discord or meetup, YouTube and Twitter as well as GitHub. The blog module is enabled. I haven't finished. I haven't started on my authors and blogs and stuff like that. We have some good opportunity to repurpose content that we do in our normal discussions, normal showcases on that updated our events using it using Claude devs pointed out or meet up and had it had a generated thing which is pretty cool and then, after last night's hacky hour literally sat down and said this is today's day. Check. Check whether the current and upcoming events are appropriate. Really cool. I envision the author's page on here.  
So one one one feedback that came from Karim was it'd be really cool if we had a website where our members just when we have that the slide, which has everyone's like GitHub information and linked in information, stuff like that we're able to effectively have like a speaker's page or something like that. So the thing I did is I took the 1o11 of two is one of threes. And, I went ahead and using Claude Dev had it go through the different notebooks and create descriptions of them and organize it per month.  
So kind of look kind of looking at it right now as almost like a yearbook of what we've been able to do and share with each other. And then I'll figure out the pipelines of getting in our. I'm working on like the pipelines of pulling in the presentations and stuff like that.  
So if we have, you know, a nice little and IA log what we've done. My thoughts are in the future that you know people are presenting or contributing labs, the repo or presentations or some like that we can collect and consolidate that stuff, but use this as a kind of a little PR thing where you know a person is presenting can author post as relevant to it and we can drive some further conversation. Leaving this one edited to open to AI crawlers and stuff like that so we can start to get in that ecosystem transparently. Thoughts? Feedback?  
**Rob | 21:39  
**I think it's a good Colin, I like that you've done this. I think it enhances visibility. It looks very professional, and I think it's cool. You did? You used Claud Deb to do it.  
**Colin McNamara | 21:51  
**Yeah, thanks. I appreciate that. The level of effort to do this.  
I mean, it's probably about four hours of going back and forth with stuff so far. I think there's a lot of opportunity for and that includes like figuring out and learning.  
So I go just continue to iterate on it and get, you know, whatever we have in there. And we can think there's some definitely some pipeline work to be done to make it a little easier. Any other feedback, suggestions, criticisms?  
**Saurabh | 22:28  
**I think it looks really cool. I mean, this probably has more documentation than the actual Langch documentation, so good work there.  
**Colin McNamara | 22:39  
**Yeah, it's pretty safe.  
Yeah, I figure over time, you know, all these things we've been showing off to each other and showing off to the world. You know it. It in many cases, shows a pattern of early adoption and innovation.  
You know, who are real, who are the actual influencers in the space and not thought leaders. And I would suggest that the work that we're doing puts us in, you know, top 5% of them.  
You know. Okay. There's anything anyone else wants to add? I'm open to it. But I say let's switch to open forum and, go from there.  
**Saurabh | 23:27  
**I have two things to share. Two quick updates.  
So, I don't know how many people, did get access to this new Model called Data JAMA, but Google just recently launched this new Model called Data GMMA, which is. Which basically ends up introducing a new concept called rig, which is called retrieval, interlevel generation.  
**Colin McNamara | 23:52  
**God. What?  
**Saurabh | 24:07  
**It's quite an interesting concept, although, what they're basically doing is like they're like, chaining stuff up, but they're doing that inside the Model itself.  
So I've basically linked. I got access to it, like early access to it, so. And they shared the research paper.  
So I have shared that research paper in the news section. I think that's where I've done that. It's an it's a pretty interesting re read because they basically end up using data commons to basically enhance answers and questions about different, you know, data retrieval questions. I will try and share the Google Collab notebooks as well. I'm not sure like how access works there, but I can try and do that. They've basically ended up sharing like two data to Google collab notebooks, one on Reagan, one on RAG. They're both quite interesting because let me just quickly share my screen, right?  
So, I think at least I think about the questions of. So like these works.  
There's the rig notebook, which is it basically has this new Model called, Data GMA, basically ends up using this, Data Commons liability. You can basically end up downloading it. But what is very interesting here is that.  
So, you know, you basically ask it to like compare, you know, demographics for Cambridge MA and Paul Ca or something of that sort. So it will. Or you ask it to basically compare like, the GDP of G20 countries, and it will basically go to Data Commons, extract the data from there and basically give you this entire, answer based on actual information from data comments, which is quite interesting.  
I mean, it's. It's. I mean, usually you wouldn't know where you can get, you know, answers from. But they basically just ingrained that data common piece and it basically just queries it and it basically, you know, gives you that answer along with like, proper, Descriptions and text and everything else.  
So I found it's quite an interesting approach. They're still pretty early stage.  
So it's not like the best answers that you get, but at least the examples that they ended up sharing. You get really good answers for those. I think if you ask it much more broader questions. I wasn't very satisfied with that. But if you ask some of these questions, like, the, answers are really good.  
Like, if somebody is doing like, good government research, just like generic research, they can do that. Like it has like COD data and stuff like that, economic data.  
So that's quite interesting. I'll try and share the Google Collab network as well. I think it's fun to play around with it.  
**Colin McNamara | 27:34  
**Yeah. I'm eager you army at Rickie.  
**Saurabh | 27:40  
**Yes, sir.  
**Ricky | 27:43  
**Hey, guys, I know I just joined. Is there any more actions? We talked about. Changed from the last meeting.  
**Colin McNamara | 28:00  
**The actions around the last meeting are. I'm gonna go out. Rob volunteered either for on site or remote testing to hook in the AV system and figure out the big room and make sure that we can take like remote audio in and make sure it comes out over the stuff. Make sure we can test out the microphones. I'll bring out my as many that I got used for Capture the Desktop and rig that up as well. Came volunteered as well. Those are the big actions. The other thing that we discussed was. There's like three screens on the setup, right? There's three the two, 22 80 inch monitors and then like 100 inch monitors and like a mega big, you know, conference size screen. I was thinking about setting up the one on one session that you're running that's concurrent with the mixer on one of the like 80 or 100 inch screens. In setting up with circular round top tables. And so that we can get the new people in. Kind of consolidated into one area that you'll be able to teach them. And I gotta figure out how to do it on the caurant.  
Like, just turn on one of the small screens for the 01:01 section. And then we'll have the new people in an area with, you know, one or two people sitting around and with them to kind of welcome them in and. And help them out. Through the things. And, you know, drive participation and make them feel welcome.  
And then when it comes to the larger event, we'll have, you know, almost like the front third dedicated to people that are new. And then just how people will cluster around the TV, right?  
And then as we turn on the big screen for the main thing, you know, everyone can like, filter in. And I was thinking about probably eight or ten. We have like twenty five signed up right now off likely 50 by when people, you know, look at their meet up for that week and so doing like whatever the equivalent round tops are.  
So just like a conference.  
**Saurabh | 29:54  
**Sweet.  
**Ricky | 29:55  
**And? And that was, just not next week, right? October 2nd, but is okay, cool, sweet.  
**Colin McNamara | 30:02  
**Yeah, it's next week. Yeah, we have that plane the what ready.  
**Ricky | 30:06  
**I'll have that, intro ready by them the intro session.  
**Colin McNamara | 30:15  
**Sweet, awesome, that's really cool.  
And then I did go over the aimug.org. If you pop over to it's still in progress, but I'm basically consolidating using Claude Deb to do the work all the stuff from our labs and creating descriptions per month of the labs. And like I took the link chain introduction and distilled it into something with a clickable link.  
So I created ALC core group with all contributors. Everyone here is a member of that group for maintainers.  
So if you want to you invert them directly, you can if you want to cut PR, you can, but you know, it's this is a space that we can collaborate on as well.  
**Ricky | 30:57  
**Three.  
Yeah, I look forward to doing that. Just, the fiscal year ends, like.  
**Saurabh | 31:06  
**Two weeks.  
**Colin McNamara | 31:08  
**Yeah, there's no stress on anything like taxes running a business, your taxes are really due at the end of where your extension is.  
**Ricky | 31:08  
**For us, so. Yeah, it's.  
**Saurabh | 31:11  
**Yeah.  
**Ricky | 31:11  
**It's a little stress for out.  
**Colin McNamara | 31:22  
**So, yeah, like, I'm very busy right now as well as I'm. I think I'm have to spend like six hours at City Hall waiting for a slot to present tonight. But yeah, there's no pressure this in time. It's just like it's there right as another place where would play around. And my thoughts were, you know, as we're onboarding new people too, they can go to URL and there's like all the things that we put in the repo. We can.  
You know. They can follow it and directly link back down to the appropriate things. Just make it easy.  
**Ricky | 31:53  
**Yeah, that's, solid. Move. Claud Dov now I really want to use it.  
**Colin McNamara | 31:56  
**Yeah, totally, yeah, and then yeah, we're in the middle of the open forum. Sorry Sam wes for interrupt or sorry for interrupting you.  
**Ricky | 32:08  
**Yeah, I'm sorry about that. Alright, just wanted to be clear on the action so I get a meeting coming up so I'm gonna drop.  
**Colin McNamara | 32:18  
**Cool yeahic not appreciate sorry interrupting you sorry.  
**Ricky | 32:18  
**Appreciate you guys.  
**Saurabh | 32:29  
**Nories I just ended up sharing, like on news all of the things I should be able to access it.  
**Colin McNamara | 32:37  
**Yeah, nice.  
**Saurabh | 32:38  
**So the reg notework, the rag network and the hugging FAS, link for the Model. So.  
**Colin McNamara | 32:46  
**Yeah, I can access it. That's really great. Okay.  
**Saurabh | 32:55  
**It's an interesting approach.  
I mean, I think the paper is more interesting than the notebook itself. I think the it's got some really interesting approaches and pieces there.  
So, yeah, I would recommend going through the paper in general.  
**Colin McNamara | 33:14  
**Yeah, to.  
**Saurabh | 33:14  
**I think that was one piece.  
So you were saying?  
**Colin McNamara | 33:20  
**No, I was just screwing with it.  
**Saurabh | 33:24  
**Okay. I think the other piece is like, I ended up coding, a linkeden post agent. So, I got some really interesting results with it.  
So I think I posted that in Showcase, which basically, like, it ends up generating, like, your entire linkeden post, like, scrapes through data, like, gets you, like, actual data, creates like a nice thumbnail for it. And yeah, I think, I mean, I basically just handed over my entire link to this particular agent and like, I mean, earlier I would have to like literally think to post on LINGEN like now this agent can like post like multiple times on link, then in a single day, I'm just really enjoying it.  
So yeah.  
**Colin McNamara | 34:18  
**That's rad. I think there's a lot of opportunity in, like, you know, we're kind of spinning up this.  
**Karim Lalani | 34:24  
**A minute.  
**Colin McNamara | 34:31  
**I'm a big believer in doing stuff before talking about stuff. There's so many people that talk all the time and then do shit, and transparently, you know, I don't think they're full of shit. Most of the. But, you know, social media is important.  
So you know, for a year we've been doing stuff and we're just starting to explore automated ways of talking about what we're doing. I'm really interested in, you know, maybe using this agent as a method for in our pipeline from, you know, what we're doing here in Austin, LA chain and mug, getting content out there. And maybe that's something that would be interesting for all. For us to explore. Thoughts?  
**Saurabh | 35:14  
**No. I completely agree. I think, so, I'm happy sharing the base notebook for it. I think, because I think this is still early days because I think this is probably going to be like the best product for trustee marketing, but it's still like trustee marketing is still like six months away. I think the idea there is still to focus on the business intelligence part of it and then from business and intelligence move to actual actions. And like trustee marketing would be another component of that particular piece.  
**Colin McNamara | 35:47  
**Hey.  
**Saurabh | 35:50  
**But II mean, this is still very raw, very unusual. And I think it's.  
I mean, I still find it very useful. The only thing right now I need to like my, access tokens and everything else is right.  
Still ingrained within the notebook, so I'll have to just clean that up and I'll be happy to share it.  
**Colin McNamara | 36:10  
**Yeah, I think that could save a lot of time for a lot of people in a group.  
**Saurabh | 36:16  
**Yeah, I mean, I'm more than happy for people to like, just, you know, use it. I mean, it gives me amount of feedback on it. But right now it's just like a notebook. I was probably thinking of spinning like a small, streamlet. Front end on top of this, but yeah, I haven't been able to do that right now. I like the idea of.  
**Karim Lalani | 36:41  
**Yeah, I like it being a notebook because then anybody in our group can sort of, you know, load it up in collab and just walk through it and see it happen. And then, of course, we can have a companion streamlet app that just does it for you. What do you think?  
**Saurabh | 36:57  
**Yeah, I mean, I was thinking of, like, just having, like, a couple of, like, streamlet. Like a section within the notebook that basically just said, launches like a streamlet. Front end from the notebook itself.  
So and the notebook can basically do the heavy liftting and then, you can just straight away, you know, just use the front end to basically on the network.  
**Colin McNamara | 37:27  
**I think this is wonderful. I think that you know, as Karim discussed, having a notebook that can people can go through a concept and then, you know, showing exploring what frameworks could be implemented into like into a pipeline, whether that's an which has been popping up a bit, you know. Review reviewed a video this morning I think Bascom posted. Showed me some of his workflow a couple sessions ago, but.  
And then you know we have our LAN graph agent graph. So all sorts of fun ways. You can start to explore it, but it's a pain point that everyone has, right? We'll have to create. We don't have to. But you know, part of business nowadays is to create a bunch of spew to put on the social media platforms. And Linked in has a lost spew and the ability to automate that and return time to everyone's schedule. That's a. That's a really powerful.  
**Saurabh | 38:18  
**America mean I can.  
**Colin McNamara | 38:19  
**To get out there.  
**Saurabh | 38:21  
**So there are two verss of it. One is like the basic, like the text version.  
And then there is, another like the one with a thumbnail and stuff like that.  
**Colin McNamara | 38:32  
**Hey.  
**Saurabh | 38:33  
**Let me share, like, another post which only does, like the base version.  
**Colin McNamara | 38:40  
**Yeah.  
Yeah. It's.  
**Saurabh | 38:47  
**I mean, so I think the thing that I really liked about it, is the fact that, you know, I'm able to search the Internet with it. And I think, that.  
So this is like another post. This is all completely created by.  
Yeah, I literally told it. Like, how can AI revolutionize revolution? Or There's something wrong with our words. Film me today. I just can't pronounce them. But how do you revolutionize, you know, data intelligence with the I.  
**Colin McNamara | 39:23  
**Six.  
**Saurabh | 39:23  
**But yeah, so it basically searched the internet, went ahead, like looked at a couple of bunch of Mckenzie Gartner reports and like, picked up data from Forbes and like, it just created this really nice post on us.  
Like. Yeah, like now we're talking. I mean, this is good.  
**Colin McNamara | 39:40  
**Two.  
**Saurabh | 39:43  
**I mean, you can still feel that this is AI generated, maybe to some extent. I mean, I agree. But what you can do with it is that you can. I've like, basically configured something called a tone. You can change the tone of your costs as well.  
So this could be like, professional and opinionated. It could be another one which is like, casual. You can have like another one with dad jokes or something like that.  
So it does all of that. So I mean, I found that really useful.  
I mean, doing all of that research and just getting the social media engine going, I feel is a big problem for a lot of people.  
**Colin McNamara | 40:30  
**Yeah, way cool. I think that starting the conversation. I wouldn't worry so much about sharing.  
You know, I wouldn't worry so much about anything. Sharing the basic concept and having an executable like a minimally viable executable notebook that people would come through would be some at a lot of value to a lot of people and continue to, drive visibility.  
**Saurabh | 40:57  
**I am happy to share this. I mean, this one. The only other thing is that this uses the flux Model for, like, image generation. I think, so that use it like a A 100 gp with him.  
**Colin McNamara | 41:11  
**Hey.  
**Saurabh | 41:13  
**I mean, you can run it, like, on AT4 GP. But, when you run it on a T4 GP, it almost takes like, 5 minutes to basically generate, like, a image on, like. Whereas if you run it on a 100g p, it literally takes like a couple of seconds.  
**Colin McNamara | 41:30  
**Nice.  
**Saurabh | 41:31  
**So I think, yeah, like just running it there. Like. Like you can get, like, pretty decent, images out of it.  
So, yeah, I think, go.  
**Colin McNamara | 41:43  
**Well, that's really exciting and I love it. You're introducing, continue to introduce concepts that save people's time in the day and allow them to more effectively generate information out to their network like that. That's really powerful.  
**Saurabh | 42:02  
**I mean. I mean, there are only two kinds of things that actually work in the world, right? Either you end up saving people a lot of money, or you end up saving people a lot of time. So.  
**Colin McNamara | 42:15  
**Time is money.  
Yeah, you can literally burn money and go make more, you burn time here it's spent the most important thing ever. Sub Jackson we are going in open form right now.  
**Rob | 42:28  
**Has gone.  
**Colin McNamara | 42:32  
**Samwise is discussing a linked in a LinkedIn post automation tool that he built or was using.  
**Saurabh | 42:41  
**That CO yeah, sorry, I was just saying that probably next week I'll try and share that notebook either during officers or during the community.  
**Colin McNamara | 42:42  
**Yeah, really cool. What other topics we have for? Go ahead, sorry.  
Yeah that sounds amazing. I appreciate you, man. And we'll be sure to get you the readback. Whether we have audio issues figured out you.  
So you don't have to wake up early if you're going to present, but I'm going to take time out of my week to spin, dedicated to making that happen. So go back to you.  
**Saurabh | 43:26  
**A pretty decl so on.  
**Colin McNamara | 43:32  
**What other proposed topics? It's. It's basically. It's open forum. Office hours right now, so speak up.  
**Jackson | 43:48  
**I don't have anything off the top of my head, just kind.  
**Karim Lalani | 43:50  
**But.  
**Colin McNamara | 44:03  
**Are there any other topics people can propose? You're on mute, Karim.  
**Karim Lalani | 44:12  
**Thank you. Good thing I started the I turn on the camera so you could.  
**Colin McNamara | 44:19  
**Yeah.  
**Karim Lalani | 44:19  
**I will be spending some time on DSPY just to see, you know, because the whole marketing speel is you don't need prompt templates. And that just feels more like a marketing spek than really what's happening because there's always templates.  
**Colin McNamara | 44:40  
**M.  
**Karim Lalani | 44:41  
**So I just want to sort of do a deep dive and figure out what the fuss is all about and see if there's ways to sort of leverage, you know, play to the strengths of the SPI and lang chain, you know, if, you know, maybe I identif situations where both could be used side by side.  
**Colin McNamara | 45:01  
**Interesting.  
**Karim Lalani | 45:02  
**So that is something that I yeah, that's on my list.  
**Colin McNamara | 45:25  
**The awkward silence pause out here.  
**Jackson | 45:29  
**Are these topics that we're wanting to add to the panel. So I'm I missed part of this. Or is this just open form?  
**Colin McNamara | 45:33  
**No, yeah, it's open form. We are done, like with the minutiae of running our group. And now it's just, you know, like I. Yes, time. But whatever you're working on, you know, open forms like office hours.  
**Karim Lalani | 45:50  
**Is there. Given that we couldn't get on sessions, will we have a transcript of this meeting, or will we have to skip this one?  
**Colin McNamara | 46:02  
**I can post a transcript of the meeting to one of our whatever is the appropriate forum.  
**Karim Lalani | 46:13  
**Usually you just tuck it into a GitHub, right, for under meeting transcripts.  
**Colin McNamara | 46:17  
**Yes, I can put on it. I'll put on I'll emerge it on under GitHub.  
**Karim Lalani | 46:21  
**Okay, perfect. Yeah. Once it's done, I'll. I'll run it through notebook element. We'll see what it comes up with.  
**Colin McNamara | 46:29  
**Yeah, sessions. And I started a new session at work.  
So it was just whatever the save sesion was somewhat walkky.  
**Saurabh | 46:36  
**Okay?  
**Colin McNamara | 46:36  
**Yeah, I like that. You're like where's the transcript and where's the [Laughter] no, you have you're playing with the podcast generation, right? And SORB is to demonstrate to talk about notebook and demonstrating abook for like social media post generation. I've been playing with the HML generation and for a website and stuff like that. And I sense that the little the building blocks are starting to come together with like a content distribution pipeline that generates from, you know, the conversations we already have. I sense it. I'm probably over and underestimating the work to bluw it altogether, but you know.  
**Saurabh | 47:20  
**Yeah, well.  
**Karim Lalani | 47:26  
**We have to start somewhere, so. And unless we and we have to start with small things anyway and then we can hopefully tie them together, sort of have a thread running through them and hopefully something interesting will come out of it that you know, something that you know, with the, combined efforts and that every everybody's putting in you know.  
So some. You know, maybe something interesting. Will? Will come out of it.  
**Colin McNamara | 47:58  
**I suspect that as we nerd out and the or nerd button like once when you dump the transcripts of notebook. LM I'm like, I see that, like in my head, I've seen it, right? It's like getting together with friends and engineering stuff and, you know, doing that like cool. I think that's down. And that's easy, right? Copywriting a post is annoying. But you know, I can definitely see that, you know, the work that we already do, that being reflected out. And I suspect there's a lot to be learned on that journey too. A lot to be learned in the journey that's incredibly relevant to other people in the world which allows us to tell a story and virtuous cycle and telling a story about telling a story digitally. You how? Meda.  
**Jackson | 49:03  
**K could you are you starting on that toll generation concept?  
**Karim Lalani | 49:09  
**That is something. Yeah, I'm gonna once I wrap up the. The current project that I have going with Claud, that is something I want to give a shot and see.  
You know, I don't want to write the code for that, but it'll be a good exercise to throw out plot DE and see how it can how it fares. But I will start doing some initial legwork in terms of identifying requirements.  
So that I can then, you know, place copy paste prompts into clot dev for different sections.  
**Jackson | 49:54  
**Is this primarily going to be like a you're gonna start with like a script to provet it out like a Jupiter notebook of some sort or.  
**Karim Lalani | 50:02  
**I haven't given it that much thought yet. It the idea is, you know, you have to bootstrap it with something, right?  
So, maybe a simple React Agent built LAN graph with maybe a couple additional steps that can look at what you have in your what tools you have in your tool set and if it doesn't find an appropriate one, you know, generates one based on the available APIs and utilities you might have access to. And then once we have that working, we can then pull in Ryan's GitHub stuff and then, you know, set that in it to get I it to GitHub and, enhance enhancements using by opening issues on GitHub.  
So it's it seems like it would be an interesting sort of journey to sort of embark on with this. You know, we can start small and then we can say, okay, what else can we do with it? What else can we do with that?  
**Jackson | 51:28  
**Yeah, once you prove that concept, like you were talking about ye.  
**Karim Lalani | 51:33  
**Because. So one idea is, you know, you're asking it to do something, and then it figures out whether it needs to build a tool, and if it does, it just does it and use uses that tool. The other thing is, rather than you ask it to do something, you just say, okay, you know, it would be nice to have these tools in my tool set. And that's where you know the whole idea behind opening up feature requests or issues sort of start come to come into play.  
So you just build me a tool that does this.  
**Colin McNamara | 52:01  
**Hey.  
**Karim Lalani | 52:06  
**It's ambitious. We'll see.  
**Colin McNamara | 52:13  
**I think it'll be cool. But that's just my. My thoughts.  
**Karim Lalani | 52:27  
**I got to prepare for my 03:00 meeting, so a great community call. Take Colin.  
**Colin McNamara | 52:33  
**No sounds good.  
**Karim Lalani | 52:33  
**I'll. I'll be on the lookout for the transcripts. And we'll see you guys next week.  
**Colin McNamara | 52:40  
**I needed to drop as well, I got 03:00. It was good talking to everyone. Thanks for all the sport, really appreciate it and I will see you all next week.