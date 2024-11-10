# Project architectury
```plaintext
sunrise_bot/
├── bot.py                   
├── config.py                
├── cogs/                    
│   ├── __init__.py          
│   ├── admin.py             
│   ├── moderation.py        
│   ├── fun.py               
│   ├── utilities.py         
│   ├── economy.py           
│   ├── music.py             
│   └── games.py             
├── utils/                   
│   ├── __init__.py          
│   ├── helpers.py           
│   ├── database.py          
│   ├── checks.py            
│   └── logging_config.py    
├── events/                  
│   ├── __init__.py          
│   ├── on_ready.py          
│   ├── on_message.py        
│   ├── on_member_join.py    
│   ├── on_member_remove.py  
│   └── error_handler.py     
├── data/                    
│   ├── banned_words.txt     
│   ├── guild_config.json    
│   ├── memes.json           
│   └── trivia_questions.json
├── logs/                    
│   ├── bot.log              
│   └── errors.log           
├── tests/                   
│   ├── __init__.py          
│   ├── test_admin.py        
│   ├── test_moderation.py   
│   ├── test_fun.py          
│   └── test_database.py     
├── requirements.txt         
├── README.md                
└── .env                     
