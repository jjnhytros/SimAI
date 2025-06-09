# core/enums/weather_types.py
from enum import Enum, auto

class WeatherType(Enum):
    """Rappresenta le condizioni meteorologiche."""
    
    # ================= CATEGORIA 1: METEO SERENO (50) =================
    CLEAR_SKY = auto()              # Cielo sereno
    SUNNY = auto()                  # Soleggiato
    MOSTLY_SUNNY = auto()           # Prevalentemente soleggiato
    PARTLY_CLOUDY = auto()          # Parzialmente nuvoloso
    HIGH_PRESSURE = auto()          # Alta pressione
    MILD = auto()                   # Temperatura mite
    PLEASANT = auto()               # Piacevole
    CALM_WINDS = auto()             # Vento calmo
    GOLDEN_HOUR = auto()            # Ora dorata
    TWILIGHT = auto()               # Crepuscolo
    STARRY_NIGHT = auto()           # Notte stellata
    MOONLIT = auto()               # Chiaro di luna
    SUNRISE = auto()                # Alba
    SUNSET = auto()                 # Tramonto
    FAIR_WEATHER = auto()           # Bel tempo
    CRISP = auto()                  # Aria frizzante
    INVIGORATING = auto()           # Aria tonificante
    TRANQUIL = auto()               # Atmosfera tranquilla
    BALMY = auto()                  # Atmosfera mite
    SUNNY_SPELL = auto()            # Schiarita
    OPTIMAL_VISIBILITY = auto()     # Visibilità ottimale
    DRY_SPELL = auto()              # Periodo secco
    SUNNY_BREEZE = auto()           # Sole e brezza
    SPRING_LIKE = auto()            # Tempo primaverile
    SUMMER_LIKE = auto()            # Tempo estivo
    AUTUMN_LIKE = auto()            # Tempo autunnale
    WARM_SPELL = auto()             # Periodo caldo
    PERFECT_WEATHER = auto()        # Tempo perfetto
    STABLE = auto()                 # Condizioni stabili
    # Aggiunte
    SUNNY_INTERVALS = auto()        # Schiarite solari
    BRIGHT = auto()                 # Luminoso
    SUNNY_WITH_HIGH_CLOUDS = auto() # Sole con nuvole alte
    SUNNY_WITH_CIRRUS = auto()      # Sole con cirri
    SUNNY_WITH_CONTRAILS = auto()   # Sole con scie di condensazione
    CLEAR_NIGHT = auto()            # Notte limpida
    RADIANT_MORNING = auto()        # Mattina radiosa
    PACIFIC = auto()                # Pacifico
    SERENE_AFTERNOON = auto()       # Pomeriggio sereno
    CALM_EVENING = auto()           # Sera calma
    STILL_NIGHT = auto()            # Notte calma
    SUNNY_PATCHES = auto()          # Chiaroscuri solari
    OPTIMUM_CLIMATE = auto()        # Clima ottimale
    PLEASANTLY_WARM = auto()        # Piacevolmente caldo
    COMFORTABLY_COOL = auto()       # Piacevolmente fresco
    REFRESHING_MORNING = auto()     # Mattina rinfrescante
    GENTLE_WEATHER = auto()         # Tempo gentile
    TRANQUIL_DAWN = auto()          # Alba tranquilla
    PEACEFUL_DUSK = auto()          # Crepuscolo pacifico
    IDYLLIC = auto()                # Atmosfera idilliaca
    
    # ================= CATEGORIA 2: PRECIPITAZIONI (50) =================
    DRIZZLE = auto()               # Pioggerellina
    RAINING = auto()               # Pioggia
    LIGHT_RAIN = auto()            # Pioggia leggera
    MODERATE_RAIN = auto()         # Pioggia moderata
    HEAVY_RAIN = auto()            # Pioggia intensa
    DOWNPOUR = auto()              # Acquazzone
    FREEZING_RAIN = auto()         # Pioggia gelata
    MIST = auto()                  # Foschia
    SPRINKLE = auto()              # Pioggerella
    RAIN_SHOWERS = auto()          # Rovesci di pioggia
    THUNDERY_RAIN = auto()         # Pioggia temporalesca
    STEADY_RAIN = auto()           # Pioggia costante
    URBAN_RAIN = auto()            # Pioggia urbana
    RAIN_AND_WIND = auto()         # Pioggia e vento
    RAIN_AT_NIGHT = auto()         # Pioggia notturna
    RAIN_MORNING = auto()          # Pioggia mattutina
    RAIN_AFTERNOON = auto()        # Pioggia pomeridiana
    RAIN_EVENING = auto()          # Pioggia serale
    WET_WEATHER = auto()           # Tempo umido
    RAINY_SPELL = auto()           # Periodo piovoso
    SOAKING_RAIN = auto()          # Pioggia battente
    RAIN_WITH_FOG = auto()         # Pioggia con nebbia
    RAIN_WITH_MIST = auto()        # Pioggia con foschia
    RAIN_WITH_DRIZZLE = auto()     # Pioggia con pioggerellina
    RAIN_WITH_SLEET = auto()       # Pioggia con nevischio
    # Aggiunte
    ISOLATED_SHOWERS = auto()      # Rovesci isolati
    SCATTERED_SHOWERS = auto()     # Rovesci sparsi
    FREQUENT_SHOWERS = auto()      # Rovesci frequenti
    PERSISTENT_RAIN = auto()       # Pioggia persistente
    INTERMITTENT_RAIN = auto()     # Pioggia intermittente
    COASTAL_RAIN = auto()          # Pioggia costiera
    MOUNTAIN_RAIN = auto()         # Pioggia montana
    VALLEY_RAIN = auto()           # Pioggia in valle
    URBAN_DOWNPOUR = auto()        # Acquazzone urbano
    RURAL_RAIN = auto()            # Pioggia rurale
    FOREST_RAIN = auto()           # Pioggia forestale
    SEA_RAIN = auto()              # Pioggia sul mare
    LAKESHORE_RAIN = auto()        # Pioggia lacustre
    RIVER_RAIN = auto()            # Pioggia fluviale
    HILLY_RAIN = auto()            # Pioggia collinare
    PLAIN_RAIN = auto()            # Pioggia in pianura
    GARDEN_RAIN = auto()           # Pioggia da giardino
    WINDOW_RAIN = auto()           # Pioggia contro i vetri
    AUTUMN_RAIN = auto()           # Pioggia autunnale
    SPRING_RAIN = auto()           # Pioggia primaverile
    SUMMER_RAIN = auto()           # Pioggia estiva
    WINTER_RAIN = auto()           # Pioggia invernale
    TROPICAL_RAIN = auto()         # Pioggia tropicale
    MONSOON_RAIN = auto()          # Pioggia monsonica
    DRENCHING = auto()             # Acqua a catinelle
    PUDDLE_FORMING = auto()        # Formazione di pozzanghere
    GUTTER_FLOWING = auto()        # Acqua nei tombini
    
    # ================= CATEGORIA 3: TEMPORALI E ESTREMI (50) =================
    STORM = auto()                 # Temporale
    THUNDERSTORM = auto()          # Temporale con tuoni
    LIGHTNING_STORM = auto()       # Temporale con fulmini
    SEVERE_STORM = auto()          # Temporale intenso
    HAIL = auto()                  # Grandine
    HAILSTORM = auto()             # Tempesta di grandine
    THUNDER = auto()               # Tuono
    LIGHTNING = auto()             # Fulmine
    ELECTRICAL_STORM = auto()      # Tempesta elettrica
    SQUALL = auto()                # Burrasca
    GUSTY_WINDS = auto()           # Raffiche di vento
    WIND_STORM = auto()            # Tempesta di vento
    DUST_STORM = auto()            # Tempesta di sabbia
    SAND_STORM = auto()            # Tempesta di sabbia
    TORNADO = auto()               # Tornado
    HURRICANE = auto()             # Uragano
    TYPHOON = auto()               # Tifone
    CYCLONE = auto()               # Ciclone
    MICROBURST = auto()            # Microburst
    DOWNBURST = auto()             # Downburst
    HAIL_SHOWER = auto()           # Rovescio di grandine
    THUNDER_AND_HAIL = auto()      # Tuoni e grandine
    THUNDER_AND_LIGHTNING = auto() # Tuoni e fulmini
    VIOLENT_STORM = auto()         # Tempesta violenta
    ELECTRICAL_RAIN = auto()       # Pioggia elettrica
    STORM_WITH_HAIL = auto()       # Temporale con grandine
    # Aggiunte
    SUPERCELL = auto()             # Supercella temporalesca
    WALL_CLOUD = auto()            # Nube a muro
    FUNNEL_CLOUD = auto()          # Nube a imbuto
    WATERSHOUT = auto()            # Tromba marina
    LANDSPOUT = auto()             # Tromba terrestre
    GUSTNADO = auto()              # Gustnado
    DUST_DEVIL = auto()            # Diavolo di sabbia
    FIRE_STORM = auto()            # Tempesta di fuoco
    ICE_STORM = auto()             # Tempesta di ghiaccio
    BLIZZARD = auto()              # Tempesta di neve
    WHITE_OUT = auto()             # Bianchimento
    THUNDERSNOW = auto()           # Neve con tuoni
    HAIL_SWATH = auto()            # Fascia di grandine
    WIND_SHEAR = auto()            # Wind shear
    DOWNPOUR_BURST = auto()        # Scolo di acquazzone
    FLASH_FLOOD = auto()           # Alluvione lampo
    STORM_SURGE = auto()           # Mareggiata
    ELECTROSTATIC_STORM = auto()   # Tempesta elettrostatica
    PLASMA_STORM = auto()          # Tempesta al plasma
    VOLCANIC_STORM = auto()        # Tempesta vulcanica
    ASH_STORM = auto()             # Tempesta di cenere
    METEOROLOGICAL_BOMB = auto()   # Bomba meteorologica
    SEISMIC_STORM = auto()         # Tempesta sismica
    GEOMAGNETIC_STORM = auto()     # Tempesta geomagnetica
    SOLAR_STORM = auto()           # Tempesta solare
    AURORA_STORM = auto()          # Tempesta aurorale
    COSMIC_STORM = auto()          # Tempesta cosmica
    
    # ================= CATEGORIA 4: FENOMENI ATMOSFERICI (50) =================
    FOGGY = auto()                 # Nebbia
    MISTY = auto()                 # Nebbioso
    HAZY = auto()                  # Foschia
    SMOGGY = auto()                # Smog
    LOW_VISIBILITY = auto()        # Scarsa visibilità
    FOG_PATCHES = auto()           # Banchi di nebbia
    THICK_FOG = auto()             # Nebbia fitta
    FREEZING_FOG = auto()          # Nebbia gelata
    FROST = auto()                 # Brina
    HOARFROST = auto()             # Brina bianca
    RIME = auto()                  # Brina da congelamento
    BLACK_ICE = auto()             # Ghiaccio nero
    ICY = auto()                   # Ghiacciato
    SLEET = auto()                 # Nevischio
    SNOWING = auto()               # Neve
    LIGHT_SNOW = auto()            # Neve leggera
    MODERATE_SNOW = auto()         # Neve moderata
    HEAVY_SNOW = auto()            # Neve intensa
    SNOW_SHOWERS = auto()          # Rovesci di neve
    SNOW_FLURRIES = auto()         # Fiocchi di neve
    SNOW_AT_NIGHT = auto()         # Neve notturna
    SNOW_MORNING = auto()          # Neve mattutina
    SNOW_AFTERNOON = auto()        # Neve pomeridiana
    SNOW_EVENING = auto()          # Neve serale
    WET_SNOW = auto()              # Neve bagnata
    DRY_SNOW = auto()              # Neve asciutta
    POWDER_SNOW = auto()           # Neve polverosa
    SNOW_SQUALL = auto()           # Bufera di neve
    SNOW_DRIFTING = auto()         # Neve che si accumula
    SNOW_COVERED = auto()          # Terreno innevato
    # Aggiunte
    ICE_PELLETS = auto()           # Granuli di ghiaccio
    GRAUPEL = auto()               # Graupel
    SNOW_GRAINS = auto()           # Granelli di neve
    DIAMOND_DUST = auto()          # Polvere di diamante
    FROST_SMOKE = auto()           # Fumo di gelo
    ICE_FOG = auto()               # Nebbia ghiacciata
    ARCTIC_SMOKE = auto()          # Fumo artico
    SEA_SMOKE = auto()             # Fumo di mare
    VALLEY_FOG = auto()            # Nebbia di valle
    RADIATION_FOG = auto()         # Nebbia da irraggiamento
    ADVECTION_FOG = auto()         # Nebbia da avvezione
    FREEZING_SPRAY = auto()        # Spruzzi gelati
    ICING = auto()                 # Formazione di ghiaccio
    GLAZE_ICE = auto()             # Ghiaccio vetrato
    RIME_ICE = auto()              # Ghiaccio brinato
    BLACK_FROST = auto()           # Brina nera
    WHITE_FROST = auto()           # Brina bianca
    PERMAFROST = auto()            # Permafrost
    SNOW_MIRAGE = auto()           # Miraggio nella neve
    ICE_RAINBOW = auto()           # Arcobaleno di ghiaccio
    SNOW_BOW = auto()              # Arcobaleno sulla neve
    HALO_EFFECT = auto()           # Effetto alone
    SUNDOG = auto()                # Parelio
    MOONDOG = auto()               # Parelio lunare
    GREEN_FLASH = auto()           # Raggio verde
    ZODIACAL_LIGHT = auto()        # Luce zodiacale

    def display_name_it(self) -> str:
        """Restituisce un nome leggibile in italiano per il tipo di meteo."""
        mapping = {
            # ================= METEO SERENO =================
            WeatherType.CLEAR_SKY: "Cielo sereno",
            WeatherType.SUNNY: "Soleggiato",
            WeatherType.MOSTLY_SUNNY: "Prevalentemente soleggiato",
            WeatherType.PARTLY_CLOUDY: "Parzialmente nuvoloso",
            WeatherType.HIGH_PRESSURE: "Alta pressione",
            WeatherType.MILD: "Temperatura mite",
            WeatherType.PLEASANT: "Piacevole",
            WeatherType.CALM_WINDS: "Vento calmo",
            WeatherType.GOLDEN_HOUR: "Ora dorata",
            WeatherType.TWILIGHT: "Crepuscolo",
            WeatherType.STARRY_NIGHT: "Notte stellata",
            WeatherType.MOONLIT: "Chiaro di luna",
            WeatherType.SUNRISE: "Alba",
            WeatherType.SUNSET: "Tramonto",
            WeatherType.FAIR_WEATHER: "Bel tempo",
            WeatherType.CRISP: "Aria frizzante",
            WeatherType.INVIGORATING: "Aria tonificante",
            WeatherType.TRANQUIL: "Atmosfera tranquilla",
            WeatherType.BALMY: "Atmosfera mite",
            WeatherType.SUNNY_SPELL: "Schiarita",
            WeatherType.OPTIMAL_VISIBILITY: "Visibilità ottimale",
            WeatherType.DRY_SPELL: "Periodo secco",
            WeatherType.SUNNY_BREEZE: "Sole e brezza",
            WeatherType.SPRING_LIKE: "Tempo primaverile",
            WeatherType.SUMMER_LIKE: "Tempo estivo",
            WeatherType.AUTUMN_LIKE: "Tempo autunnale",
            WeatherType.WARM_SPELL: "Periodo caldo",
            WeatherType.PERFECT_WEATHER: "Tempo perfetto",
            WeatherType.STABLE: "Condizioni stabili",
            WeatherType.SUNNY_INTERVALS: "Schiarite solari",
            WeatherType.BRIGHT: "Luminoso",
            WeatherType.SUNNY_WITH_HIGH_CLOUDS: "Sole con nuvole alte",
            WeatherType.SUNNY_WITH_CIRRUS: "Sole con cirri",
            WeatherType.SUNNY_WITH_CONTRAILS: "Sole con scie di condensazione",
            WeatherType.CLEAR_NIGHT: "Notte limpida",
            WeatherType.RADIANT_MORNING: "Mattina radiosa",
            WeatherType.PACIFIC: "Pacifico",
            WeatherType.SERENE_AFTERNOON: "Pomeriggio sereno",
            WeatherType.CALM_EVENING: "Sera calma",
            WeatherType.STILL_NIGHT: "Notte calma",
            WeatherType.SUNNY_PATCHES: "Chiaroscuri solari",
            WeatherType.OPTIMUM_CLIMATE: "Clima ottimale",
            WeatherType.PLEASANTLY_WARM: "Piacevolmente caldo",
            WeatherType.COMFORTABLY_COOL: "Piacevolmente fresco",
            WeatherType.REFRESHING_MORNING: "Mattina rinfrescante",
            WeatherType.GENTLE_WEATHER: "Tempo gentile",
            WeatherType.TRANQUIL_DAWN: "Alba tranquilla",
            WeatherType.PEACEFUL_DUSK: "Crepuscolo pacifico",
            WeatherType.IDYLLIC: "Atmosfera idilliaca",
            
            # ================= PRECIPITAZIONI =================
            WeatherType.DRIZZLE: "Pioggerellina",
            WeatherType.RAINING: "Pioggia",
            WeatherType.LIGHT_RAIN: "Pioggia leggera",
            WeatherType.MODERATE_RAIN: "Pioggia moderata",
            WeatherType.HEAVY_RAIN: "Pioggia intensa",
            WeatherType.DOWNPOUR: "Acquazzone",
            WeatherType.FREEZING_RAIN: "Pioggia gelata",
            WeatherType.MIST: "Foschia",
            WeatherType.SPRINKLE: "Pioggerella",
            WeatherType.RAIN_SHOWERS: "Rovesci di pioggia",
            WeatherType.THUNDERY_RAIN: "Pioggia temporalesca",
            WeatherType.STEADY_RAIN: "Pioggia costante",
            WeatherType.URBAN_RAIN: "Pioggia urbana",
            WeatherType.RAIN_AND_WIND: "Pioggia e vento",
            WeatherType.RAIN_AT_NIGHT: "Pioggia notturna",
            WeatherType.RAIN_MORNING: "Pioggia mattutina",
            WeatherType.RAIN_AFTERNOON: "Pioggia pomeridiana",
            WeatherType.RAIN_EVENING: "Pioggia serale",
            WeatherType.WET_WEATHER: "Tempo umido",
            WeatherType.RAINY_SPELL: "Periodo piovoso",
            WeatherType.SOAKING_RAIN: "Pioggia battente",
            WeatherType.RAIN_WITH_FOG: "Pioggia con nebbia",
            WeatherType.RAIN_WITH_MIST: "Pioggia con foschia",
            WeatherType.RAIN_WITH_DRIZZLE: "Pioggia con pioggerellina",
            WeatherType.RAIN_WITH_SLEET: "Pioggia con nevischio",
            WeatherType.ISOLATED_SHOWERS: "Rovesci isolati",
            WeatherType.SCATTERED_SHOWERS: "Rovesci sparsi",
            WeatherType.FREQUENT_SHOWERS: "Rovesci frequenti",
            WeatherType.PERSISTENT_RAIN: "Pioggia persistente",
            WeatherType.INTERMITTENT_RAIN: "Pioggia intermittente",
            WeatherType.COASTAL_RAIN: "Pioggia costiera",
            WeatherType.MOUNTAIN_RAIN: "Pioggia montana",
            WeatherType.VALLEY_RAIN: "Pioggia in valle",
            WeatherType.URBAN_DOWNPOUR: "Acquazzone urbano",
            WeatherType.RURAL_RAIN: "Pioggia rurale",
            WeatherType.FOREST_RAIN: "Pioggia forestale",
            WeatherType.SEA_RAIN: "Pioggia sul mare",
            WeatherType.LAKESHORE_RAIN: "Pioggia lacustre",
            WeatherType.RIVER_RAIN: "Pioggia fluviale",
            WeatherType.HILLY_RAIN: "Pioggia collinare",
            WeatherType.PLAIN_RAIN: "Pioggia in pianura",
            WeatherType.GARDEN_RAIN: "Pioggia da giardino",
            WeatherType.WINDOW_RAIN: "Pioggia contro i vetri",
            WeatherType.AUTUMN_RAIN: "Pioggia autunnale",
            WeatherType.SPRING_RAIN: "Pioggia primaverile",
            WeatherType.SUMMER_RAIN: "Pioggia estiva",
            WeatherType.WINTER_RAIN: "Pioggia invernale",
            WeatherType.TROPICAL_RAIN: "Pioggia tropicale",
            WeatherType.MONSOON_RAIN: "Pioggia monsonica",
            WeatherType.DRENCHING: "Acqua a catinelle",
            WeatherType.PUDDLE_FORMING: "Formazione di pozzanghere",
            WeatherType.GUTTER_FLOWING: "Acqua nei tombini",
            
            # ================= TEMPORALI E ESTREMI =================
            WeatherType.STORM: "Temporale",
            WeatherType.THUNDERSTORM: "Temporale con tuoni",
            WeatherType.LIGHTNING_STORM: "Temporale con fulmini",
            WeatherType.SEVERE_STORM: "Temporale intenso",
            WeatherType.HAIL: "Grandine",
            WeatherType.HAILSTORM: "Tempesta di grandine",
            WeatherType.THUNDER: "Tuono",
            WeatherType.LIGHTNING: "Fulmine",
            WeatherType.ELECTRICAL_STORM: "Tempesta elettrica",
            WeatherType.SQUALL: "Burrasca",
            WeatherType.GUSTY_WINDS: "Raffiche di vento",
            WeatherType.WIND_STORM: "Tempesta di vento",
            WeatherType.DUST_STORM: "Tempesta di polvere",
            WeatherType.SAND_STORM: "Tempesta di sabbia",
            WeatherType.TORNADO: "Tornado",
            WeatherType.HURRICANE: "Uragano",
            WeatherType.TYPHOON: "Tifone",
            WeatherType.CYCLONE: "Ciclone",
            WeatherType.MICROBURST: "Microburst",
            WeatherType.DOWNBURST: "Downburst",
            WeatherType.HAIL_SHOWER: "Rovescio di grandine",
            WeatherType.THUNDER_AND_HAIL: "Tuoni e grandine",
            WeatherType.THUNDER_AND_LIGHTNING: "Tuoni e fulmini",
            WeatherType.VIOLENT_STORM: "Tempesta violenta",
            WeatherType.ELECTRICAL_RAIN: "Pioggia elettrica",
            WeatherType.STORM_WITH_HAIL: "Temporale con grandine",
            WeatherType.SUPERCELL: "Supercella temporalesca",
            WeatherType.WALL_CLOUD: "Nube a muro",
            WeatherType.FUNNEL_CLOUD: "Nube a imbuto",
            WeatherType.WATERSHOUT: "Tromba marina",
            WeatherType.LANDSPOUT: "Tromba terrestre",
            WeatherType.GUSTNADO: "Gustnado",
            WeatherType.DUST_DEVIL: "Diavolo di sabbia",
            WeatherType.FIRE_STORM: "Tempesta di fuoco",
            WeatherType.ICE_STORM: "Tempesta di ghiaccio",
            WeatherType.BLIZZARD: "Tempesta di neve",
            WeatherType.WHITE_OUT: "Bianchimento",
            WeatherType.THUNDERSNOW: "Neve con tuoni",
            WeatherType.HAIL_SWATH: "Fascia di grandine",
            WeatherType.WIND_SHEAR: "Wind shear",
            WeatherType.DOWNPOUR_BURST: "Scolo di acquazzone",
            WeatherType.FLASH_FLOOD: "Alluvione lampo",
            WeatherType.STORM_SURGE: "Mareggiata",
            WeatherType.ELECTROSTATIC_STORM: "Tempesta elettrostatica",
            WeatherType.PLASMA_STORM: "Tempesta al plasma",
            WeatherType.VOLCANIC_STORM: "Tempesta vulcanica",
            WeatherType.ASH_STORM: "Tempesta di cenere",
            WeatherType.METEOROLOGICAL_BOMB: "Bomba meteorologica",
            WeatherType.SEISMIC_STORM: "Tempesta sismica",
            WeatherType.GEOMAGNETIC_STORM: "Tempesta geomagnetica",
            WeatherType.SOLAR_STORM: "Tempesta solare",
            WeatherType.AURORA_STORM: "Tempesta aurorale",
            WeatherType.COSMIC_STORM: "Tempesta cosmica",
            
            # ================= FENOMENI ATMOSFERICI =================
            WeatherType.FOGGY: "Nebbia",
            WeatherType.MISTY: "Nebbia leggera",
            WeatherType.HAZY: "Foschia",
            WeatherType.SMOGGY: "Smog",
            WeatherType.LOW_VISIBILITY: "Scarsa visibilità",
            WeatherType.FOG_PATCHES: "Banchi di nebbia",
            WeatherType.THICK_FOG: "Nebbia fitta",
            WeatherType.FREEZING_FOG: "Nebbia gelata",
            WeatherType.FROST: "Brina",
            WeatherType.HOARFROST: "Brina bianca",
            WeatherType.RIME: "Brina da congelamento",
            WeatherType.BLACK_ICE: "Ghiaccio nero",
            WeatherType.ICY: "Ghiacciato",
            WeatherType.SLEET: "Nevischio",
            WeatherType.SNOWING: "Neve",
            WeatherType.LIGHT_SNOW: "Neve leggera",
            WeatherType.MODERATE_SNOW: "Neve moderata",
            WeatherType.HEAVY_SNOW: "Neve intensa",
            WeatherType.SNOW_SHOWERS: "Rovesci di neve",
            WeatherType.SNOW_FLURRIES: "Fiocchi di neve",
            WeatherType.SNOW_AT_NIGHT: "Neve notturna",
            WeatherType.SNOW_MORNING: "Neve mattutina",
            WeatherType.SNOW_AFTERNOON: "Neve pomeridiana",
            WeatherType.SNOW_EVENING: "Neve serale",
            WeatherType.WET_SNOW: "Neve bagnata",
            WeatherType.DRY_SNOW: "Neve asciutta",
            WeatherType.POWDER_SNOW: "Neve polverosa",
            WeatherType.SNOW_SQUALL: "Bufera di neve",
            WeatherType.SNOW_DRIFTING: "Neve che si accumula",
            WeatherType.SNOW_COVERED: "Terreno innevato",
            WeatherType.ICE_PELLETS: "Granuli di ghiaccio",
            WeatherType.GRAUPEL: "Graupel",
            WeatherType.SNOW_GRAINS: "Granelli di neve",
            WeatherType.DIAMOND_DUST: "Polvere di diamante",
            WeatherType.FROST_SMOKE: "Fumo di gelo",
            WeatherType.ICE_FOG: "Nebbia ghiacciata",
            WeatherType.ARCTIC_SMOKE: "Fumo artico",
            WeatherType.SEA_SMOKE: "Fumo di mare",
            WeatherType.VALLEY_FOG: "Nebbia di valle",
            WeatherType.RADIATION_FOG: "Nebbia da irraggiamento",
            WeatherType.ADVECTION_FOG: "Nebbia da avvezione",
            WeatherType.FREEZING_SPRAY: "Spruzzi gelati",
            WeatherType.ICING: "Formazione di ghiaccio",
            WeatherType.GLAZE_ICE: "Ghiaccio vetrato",
            WeatherType.RIME_ICE: "Ghiaccio brinato",
            WeatherType.BLACK_FROST: "Brina nera",
            WeatherType.WHITE_FROST: "Brina bianca",
            WeatherType.PERMAFROST: "Permafrost",
            WeatherType.SNOW_MIRAGE: "Miraggio nella neve",
            WeatherType.ICE_RAINBOW: "Arcobaleno di ghiaccio",
            WeatherType.SNOW_BOW: "Arcobaleno sulla neve",
            WeatherType.HALO_EFFECT: "Effetto alone",
            WeatherType.SUNDOG: "Parelio",
            WeatherType.MOONDOG: "Parelio lunare",
            WeatherType.GREEN_FLASH: "Raggio verde",
            WeatherType.ZODIACAL_LIGHT: "Luce zodiacale",
        }
        return mapping.get(self, self.name.replace("_", " ").title())