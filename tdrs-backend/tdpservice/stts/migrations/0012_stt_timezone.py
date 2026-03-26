from django.db import migrations, models


# Mapping of stt_code -> IANA timezone for all states, territories, and tribes.
# For multi-timezone states, the state capital's timezone is used.
# Tribes get their own explicit timezone (e.g., Navajo Nation observes DST
# unlike the rest of Arizona).
STT_CODE_TIMEZONE_MAP = {
    # === States (2-digit codes) ===
    "01": "America/Chicago",            # Alabama
    "02": "America/Anchorage",          # Alaska
    "04": "America/Phoenix",            # Arizona (no DST)
    "05": "America/Chicago",            # Arkansas
    "06": "America/Los_Angeles",        # California
    "08": "America/Denver",             # Colorado
    "09": "America/New_York",           # Connecticut
    "10": "America/New_York",           # Delaware
    "11": "America/New_York",           # District of Columbia
    "12": "America/New_York",           # Florida (capital: Tallahassee, Eastern)
    "13": "America/New_York",           # Georgia
    "15": "Pacific/Honolulu",           # Hawaii
    "16": "America/Boise",             # Idaho
    "17": "America/Chicago",            # Illinois
    "18": "America/Indiana/Indianapolis",  # Indiana
    "19": "America/Chicago",            # Iowa
    "20": "America/Chicago",            # Kansas
    "21": "America/New_York",           # Kentucky (capital: Frankfort, Eastern)
    "22": "America/Chicago",            # Louisiana
    "23": "America/New_York",           # Maine
    "24": "America/New_York",           # Maryland
    "25": "America/New_York",           # Massachusetts
    "26": "America/Detroit",            # Michigan
    "27": "America/Chicago",            # Minnesota
    "28": "America/Chicago",            # Mississippi
    "29": "America/Chicago",            # Missouri
    "30": "America/Denver",             # Montana
    "31": "America/Chicago",            # Nebraska
    "32": "America/Los_Angeles",        # Nevada (capital: Carson City, Pacific)
    "33": "America/New_York",           # New Hampshire
    "34": "America/New_York",           # New Jersey
    "35": "America/Denver",             # New Mexico
    "36": "America/New_York",           # New York
    "37": "America/New_York",           # North Carolina
    "38": "America/Chicago",            # North Dakota (capital: Bismarck, Central)
    "39": "America/New_York",           # Ohio
    "40": "America/Chicago",            # Oklahoma
    "41": "America/Los_Angeles",        # Oregon (capital: Salem, Pacific)
    "42": "America/New_York",           # Pennsylvania
    "44": "America/New_York",           # Rhode Island
    "45": "America/New_York",           # South Carolina
    "46": "America/Chicago",            # South Dakota (capital: Pierre, Central)
    "47": "America/Chicago",            # Tennessee (capital: Nashville, Central)
    "48": "America/Chicago",            # Texas (capital: Austin, Central)
    "49": "America/Denver",             # Utah
    "50": "America/New_York",           # Vermont
    "51": "America/New_York",           # Virginia
    "53": "America/Los_Angeles",        # Washington
    "54": "America/New_York",           # West Virginia
    "55": "America/Chicago",            # Wisconsin
    "56": "America/Denver",             # Wyoming

    # === Territories ===
    "66": "Pacific/Guam",               # Guam
    "72": "America/Puerto_Rico",        # Puerto Rico
    "78": "America/Virgin",             # Virgin Islands

    # === Tribes (3-digit codes) ===
    # Alaska tribes
    "805": "America/Anchorage",         # Association of Village Council Presidents
    "808": "America/Anchorage",         # Bristol Bay Native Association
    "811": "America/Anchorage",         # Central Council of Tlingit and Haida
    "807": "America/Anchorage",         # Cook Inlet Tribal Council
    "812": "America/Anchorage",         # Kodiak Area Native Assoc.
    "804": "America/Anchorage",         # Maniilaq Association
    "806": "America/Anchorage",         # Tanana Chiefs Conference

    # Arizona tribes
    "103": "America/Phoenix",           # Hopi Tribe (no DST)
    "167": "America/Denver",            # Navajo Nation (observes DST)
    "188": "America/Phoenix",           # Pascua Yaqui Tribe (no DST)
    "248": "America/Phoenix",           # Salt River - Pima Maricopa (no DST)
    "250": "America/Phoenix",           # San Carlos Apache (no DST)
    "322": "America/Phoenix",           # White Mountain Apache (no DST)

    # California tribes
    "517": "America/Los_Angeles",       # Federated Indians of Graton Rancheria
    "102": "America/Los_Angeles",       # Hoopa Valley Tribe
    "120": "America/Los_Angeles",       # Karuk Tribe
    "163": "America/Los_Angeles",       # Morongo Band of Mission Indians
    "172": "America/Los_Angeles",       # Northfork Rancheria of Mono Indians
    "514": "America/Los_Angeles",       # Owens Valley Career Development Center
    "193": "America/Los_Angeles",       # Pechanga Band of Luiseno Mission Indians
    "520": "America/Los_Angeles",       # Robinson Rancheria
    "241": "America/Los_Angeles",       # Round Valley Indian Tribes
    "262": "America/Los_Angeles",       # Scotts Valley Band of Pomo Indians
    "270": "America/Los_Angeles",       # Shingle Springs Band of Miwok Indians
    "279": "America/Los_Angeles",       # Soboba Band of Luiseno Indians
    "501": "America/Los_Angeles",       # Southern California Tribal Chairmen's Assoc.
    "278": "America/Los_Angeles",       # Tolowa Dee-ni' Nation
    "513": "America/Los_Angeles",       # Torres Martinez Desert Cahuilla Indians
    "307": "America/Los_Angeles",       # Tuolumne Band of Me-Wuk Indians
    "333": "America/Los_Angeles",       # Yurok Tribe

    # Idaho tribes
    "050": "America/Boise",             # Coeur d'Alene Tribe
    "168": "America/Boise",             # Nez Perce Tribe
    "273": "America/Boise",             # Shoshone-Bannock Tribes

    # Kansas tribes
    "205": "America/Chicago",           # Prairie Band Potawatomi Nation

    # Minnesota tribes
    "405": "America/Chicago",           # Mille Lacs Band of Ojibwe
    "234": "America/Chicago",           # Red Lake Band of Chippewa Indians

    # Mississippi tribes
    "158": "America/Chicago",           # Mississippi Band of Choctaw Indians

    # Montana tribes
    "020": "America/Denver",            # Blackfeet Nation
    "043": "America/Denver",            # Chippewa-Cree Indians of Rocky Boy's
    "054": "America/Denver",            # Confederated Salish & Kootenai Tribes
    "086": "America/Denver",            # Fort Belknap Indian Community Council

    # Nebraska tribes
    "175": "America/Chicago",           # Omaha Tribe of Nebraska
    "324": "America/Chicago",           # Winnebago Tribe of Nebraska
    "259": "America/Chicago",           # Santee Sioux Nation

    # Nevada tribes
    "321": "America/Los_Angeles",       # Washoe Tribe of Nevada and California

    # New Mexico tribes
    "334": "America/Denver",            # Pueblo of Zuni
    "221": "America/Denver",            # Santo Domingo Pueblo

    # North Carolina tribes
    "078": "America/New_York",          # Eastern Band of Cherokee Indians

    # Oklahoma tribes
    "165": "America/Chicago",           # Muscogee Creek Nation
    "179": "America/Chicago",           # Osage Nation of Oklahoma
    "038": "America/Chicago",           # Cherokee Nation

    # Oregon tribes
    "060": "America/Los_Angeles",       # Confederated Tribes of Siletz Indians
    "129": "America/Los_Angeles",       # Klamath Tribes

    # South Dakota tribes
    "275": "America/Chicago",           # Sisseton-Wahpeton Oyate

    # Washington tribes
    "056": "America/Los_Angeles",       # Confederated Tribes of Colville Reservation
    "142": "America/Los_Angeles",       # Lower Elwha Klallam Tribe
    "144": "America/Los_Angeles",       # Lummi Nation
    "170": "America/Los_Angeles",       # Nooksack Indian Tribe
    "203": "America/Los_Angeles",       # Port Gamble S'Klallam Tribe
    "230": "America/Los_Angeles",       # Quileute Tribe
    "231": "America/Los_Angeles",       # Quinault Indian Nation
    "504": "America/Los_Angeles",       # South Puget Inter-Tribal Planning Agency
    "282": "America/Los_Angeles",       # Spokane Tribe of Indians
    "305": "America/Los_Angeles",       # Tulalip Tribes
    "315": "America/Los_Angeles",       # Upper Skagit Indian Tribe
    "290": "America/Los_Angeles",       # Suquamish Indian Tribe

    # Wisconsin tribes
    "012": "America/Chicago",           # Bad River Band of Lake Superior Chippewa
    "085": "America/Chicago",           # Forest County Potawatomi Community
    "133": "America/Chicago",           # Lac Courte Oreilles Band
    "134": "America/Chicago",           # Lac du Flambeau Band
    "151": "America/Chicago",           # Menominee Indian Tribe of Wisconsin
    "177": "America/Chicago",           # Oneida Nation of Wisconsin
    "233": "America/Chicago",           # Red Cliff Band
    "280": "America/Chicago",           # Sokaogon Chippewa Community
    "287": "America/Chicago",           # Stockbridge-Munsee Community

    # Wyoming tribes
    "272": "America/Denver",            # Eastern Shoshone Tribe
    "008": "America/Denver",            # Northern Arapaho Tribe
}


def populate_timezones(apps, schema_editor):
    STT = apps.get_model('stts', 'STT')
    for stt in STT.objects.all():
        tz = STT_CODE_TIMEZONE_MAP.get(stt.stt_code)
        if tz:
            stt.timezone = tz
            stt.save(update_fields=['timezone'])


def reverse_timezones(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('stts', '0011_add_region_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='stt',
            name='timezone',
            field=models.CharField(blank=True, default='America/New_York', max_length=63),
        ),
        migrations.RunPython(populate_timezones, reverse_timezones),
    ]
