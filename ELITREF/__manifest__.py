# See LICENSE file for full copyright and licensing details.

{
    "name": 'Game Referee', 
    "version": "14.0.1.0.0",
    "author": "",
    "category": "Tools",
    "depends": '',
    "sequence": -10,
    "data": [
      
        "security/ir.model.access.csv",
        "data/data.xml",
        "views/organization_view.xml",
        "views/event_view.xml",
        "views/teams_view.xml",
        "views/referees_view.xml",
        "views/fans_view.xml",
        "views/coach_view.xml",
        "views/offical_book_view.xml",
        "views/match_view.xml",
        "views/location_view.xml",
        "views/court_types.xml",


        # 'wizard/location.xml',
        # 'wizard/sport_type.xml',
       
    ],
    "installable":True,
    "auto_install":False,
    "application": True,
}
