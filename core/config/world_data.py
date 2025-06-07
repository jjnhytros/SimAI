# core/config/world_data.py
"""
Definisce la struttura del mondo di gioco, i distretti e le locazioni specifiche.
Questo file serve come "database" per la generazione del mondo nella classe Simulation.
"""
from core.enums import LocationType

WORLD_DISTRICTS = {
    "La Cittadella": {
        "description": "Il cuore civico e governativo di Anthalys. Architettura monumentale e ampie piazze.",
        "tags": ["governo", "politica", "formale"],
        "locations": [
            {"name": "Palazzo del Governatore", "type": LocationType.GOVERNOR_PALACE},
            {"name": "Parlamento di Anthalys", "type": LocationType.PARLIAMENT_BUILDING},
            {"name": "Tribunale Supremo", "type": LocationType.COURTHOUSE},
            {"name": "Sede della Banca Centrale", "type": LocationType.CENTRAL_BANK_HQ},
            {"name": "Dipartimenti Amministrativi", "type": LocationType.GOVERNMENT_OFFICE},
            {"name": "Archivio Nazionale di Anthalys", "type": LocationType.NATIONAL_ARCHIVE},
            {"name": "Auditorium Civico 'La Voce'", "type": LocationType.CIVIC_AUDITORIUM},
        ]
    },
    "Quartiere delle Muse": {
        "description": "L'anima artistica e storica della città, con gallerie, teatri e caffè letterari.",
        "tags": ["arte", "cultura", "storia", "bohémien"],
        "locations": [
            {"name": "Grande Museo di Anthalys", "type": LocationType.MUSEUM},
            {"name": "Biblioteca Pubblica Centrale", "type": LocationType.PUBLIC_LIBRARY},
            {"name": "Teatro dell'Opera 'La Lirica'", "type": LocationType.THEATER_VENUE},
            {"name": "Conservatorio Musicale", "type": LocationType.CONSERVATORY},
            {"name": "Galleria d'Arte 'Visioni'", "type": LocationType.ART_GALLERY},
            {"name": "Jazz Club 'La Nota Blu'", "type": LocationType.MUSIC_VENUE_SMALL},
            {"name": "Cinema d'Essai 'Luce'", "type": LocationType.INDEPENDENT_CINEMA},
            {"name": "Caffè 'Il Ritrovo degli Artisti'", "type": LocationType.CAFE},
        ]
    },
    "Via Aeterna": {
        "description": "Il distretto finanziario e del lusso, con grattacieli e negozi esclusivi.",
        "tags": ["shopping", "lusso", "business", "moderno", "finanza"],
        "locations": [
            {"name": "Grandi Magazzini 'Aeterna'", "type": LocationType.DEPARTMENT_STORE},
            {"name": "Boutique 'Diamante'", "type": LocationType.LUXURY_SHOP},
            {"name": "Torre AION", "type": LocationType.CORPORATE_HQ_TOWER},
            {"name": "Borsa di Anthalys", "type": LocationType.STOCK_EXCHANGE},
            {"name": "Ristorante 'Cima'", "type": LocationType.FANCY_RESTAURANT},
            {"name": "SkyLounge 28", "type": LocationType.ROOFTOP_BAR},
        ]
    },
    "Il Complesso del Salice Argenteo": {
        "description": "Un'oasi di tranquillità dedicata alla salute, al benessere e alla ricerca scientifica.",
        "tags": ["salute", "scienza", "ricerca", "tranquillo"],
        "locations": [
            {"name": "Ospedale Centrale di Anthalys", "type": LocationType.HOSPITAL},
            {"name": "Clinica Pediatrica 'La Cicogna'", "type": LocationType.CHILDREN_HOSPITAL},
            {"name": "Istituto di Ricerca G.A.O.", "type": LocationType.GAO_RESEARCH_INSTITUTE},
            {"name": "Clinica 'Mente Serena'", "type": LocationType.MENTAL_HEALTH_CLINIC},
            {"name": "Centro di Riabilitazione", "type": LocationType.REHABILITATION_CENTER},
            {"name": "Farmacia Centrale", "type": LocationType.PHARMACY},
            {"name": "Centro Donazioni Sangue", "type": LocationType.BLOOD_DONATION_CENTER},
        ]
    },
    "La Loggia del Sapere": {
        "description": "Il campus universitario per le discipline umanistiche, sociali e artistiche.",
        "tags": ["università", "studio", "giovani", "cultura"],
        "locations": [
            {"name": "Facoltà di Giurisprudenza", "type": LocationType.UNIVERSITY_FACULTY_LAW},
            {"name": "Facoltà di Lettere e Filosofia", "type": LocationType.UNIVERSITY_FACULTY_ARTS},
            {"name": "Edificio Unione Studentesca", "type": LocationType.STUDENT_UNION_BUILDING},
            {"name": "Dormitori della Loggia", "type": LocationType.UNIVERSITY_DORMITORY},
            {"name": "Biblioteca Umanistica", "type": LocationType.UNIVERSITY_LIBRARY},
            {"name": "Caffè 'Il Pensatore'", "type": LocationType.CAMPUS_CAFE},
        ]
    },
    "Porto di Levante": {
        "description": "Il motore industriale e logistico di Anthalys, attivo 28 ore su 28.",
        "tags": ["industria", "logistica", "lavoro", "porto"],
        "locations": [
            {"name": "Accesso Magazzini AION", "type": LocationType.AION_WAREHOUSE_ACCESS},
            {"name": "Banchine di Carico 1-12", "type": LocationType.CARGO_DOCKS},
            {"name": "Fabbrica 'Synth-Tessile'", "type": LocationType.FACTORY},
            {"name": "Ufficio Doganale del Porto", "type": LocationType.CUSTOMS_OFFICE},
            {"name": "Mensa dei Lavoratori Portuali", "type": LocationType.WORKERS_CANTEEN},
        ]
    },
    "Giardini Sospesi": {
        "description": "Il polmone verde e il cuore ricreativo della città, con spazi per tutti.",
        "tags": ["parco", "natura", "svago", "relax", "famiglia"],
        "locations": [
            {"name": "Anfiteatro del Lago", "type": LocationType.AMPHITHEATER},
            {"name": "Serra Botanica di Anthalys", "type": LocationType.BOTANICAL_GARDEN},
            {"name": "Orti Comunitari", "type": LocationType.COMMUNITY_GARDEN},
            {"name": "Caffè del Lago", "type": LocationType.LAKE_CAFE},
            {"name": "Grande Area Giochi", "type": LocationType.PLAYGROUND},
            {"name": "Collina del Grande Albero", "type": LocationType.GREAT_TREE_HILL},
        ]
    },
    "Borgo Antico": {
        "description": "Il quartiere collinare della 'vecchia ricchezza', esclusivo e storico.",
        "tags": ["residenziale", "lusso", "storico", "tranquillo"],
        "locations": [
            {"name": "Villa 'Eredità'", "type": LocationType.RESIDENTIAL_VILLA},
            {"name": "Condominio 'Le Terrazze'", "type": LocationType.RESIDENTIAL_LUXURY_CONDO_SMALL},
            {"name": "Club Benessere 'Olimpo'", "type": LocationType.EXCLUSIVE_HEALTH_CLUB},
            {"name": "Gastronomia 'Il Palato Fino'", "type": LocationType.GOURMET_FOOD_STORE},
            {"name": "Il Vecchio Castello di Anthalys", "type": LocationType.HISTORICAL_CASTLE},
        ]
    },
    "Solara": {
        "description": "Il quartiere del futuro: sostenibile, tecnologico e comunitario.",
        "tags": ["residenziale", "moderno", "ecologia", "comunità"],
        "locations": [
            {"name": "Casa 'Eco-Pod 1'", "type": LocationType.RESIDENTIAL_ECO_HOUSE},
            {"name": "Condominio 'Girasole'", "type": LocationType.RESIDENTIAL_ECO_CONDO_MEDIUM},
            {"name": "Hub Comunitario di Solara", "type": LocationType.COMMUNITY_HUB},
            {"name": "Negozio 'Spreco Zero'", "type": LocationType.ZERO_WASTE_STORE},
        ]
    },
    "Nido del Fiume": {
        "description": "Il tranquillo e amichevole sobborgo per le famiglie.",
        "tags": ["residenziale", "famiglia", "bambini", "suburbano"],
        "locations": [
            {"name": "Villetta al 12 di Via Salice", "type": LocationType.RESIDENTIAL_TOWNHOUSE},
            {"name": "Palazzina 'I Gelsi'", "type": LocationType.RESIDENTIAL_APARTMENT_BUILDING_SMALL},
            {"name": "Scuola Primaria 'Il Nido'", "type": LocationType.SCHOOL},
            {"name": "Supermercato 'Il Carrello Pieno'", "type": LocationType.SUPERMARKET},
            {"name": "Piscina Comunale", "type": LocationType.COMMUNITY_POOL},
        ]
    },
    "Il Crocevia dei Mercanti": {
        "description": "Il distretto più vibrante, caotico e multiculturale della città.",
        "tags": ["mercato", "multiculturale", "cibo", "artigianato"],
        "locations": [
            {"name": "Il Grande Mercato", "type": LocationType.OPEN_AIR_MARKET},
            {"name": "Bottega del Vasaio", "type": LocationType.ARTISAN_SHOP},
            {"name": "Ristorante 'Le Spezie Lontane'", "type": LocationType.ETHNIC_RESTAURANT},
            {"name": "Ostello del Viandante", "type": LocationType.HOSTEL},
            {"name": "Appartamento sopra la Sartoria", "type": LocationType.RESIDENTIAL_APT_ABOVE_SHOP},
        ]
    },
    "L'Arena": {
        "description": "Il tempio dell'intrattenimento di massa e della passione sportiva.",
        "tags": ["sport", "eventi", "concerti", "folla"],
        "locations": [
            {"name": "Stadio 'Arena Fusion' di Anthalys", "type": LocationType.STADIUM},
            {"name": "Palazzetto dello Spettacolo", "type": LocationType.INDOOR_ARENA},
            {"name": "Museo dello Sport", "type": LocationType.SPORTS_MUSEUM},
            {"name": "Bar 'Il Terzo Tempo'", "type": LocationType.SPORTS_BAR},
            {"name": "Negozio Ufficiale 'Titani di Anthalys'", "type": LocationType.TEAM_MERCHANDISE_STORE},
        ]
    },
}