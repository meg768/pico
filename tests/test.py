# coding=utf8
# the above tag defines encoding for this document and is for Python 2.x compatibility

import re

regex = r"<pubDate>(.*?)</pubDate>"

test_str = ("        \n"
	"<rss version=\"2.0\">\n"
	"  <channel>\n"
	"    <title>Expressen: Nyheter</title>\n"
	"    <link>https://www.expressen.se/</link>\n"
	"    <description>Sveriges bästa nyhetssajt med nyheter, sport och nöje!</description>\n"
	"    <copyright>Copyright, AB Kvällstidningen Expressen</copyright>\n"
	"    <managingEditor>klas.granstrom@expressen.se (Klas Granström)</managingEditor>\n"
	"    <image>\n"
	"      <url>https://www.expressen.se/Static/images/rss/getting_rss.png</url>\n"
	"      <title>Expressen: Nyheter</title>\n"
	"      <link>https://www.expressen.se/</link>\n"
	"    </image>\n"
	"    <item>\n"
	"      <guid isPermaLink=\"true\">https://www.expressen.se/nyheter/misstankt-foremal-i-otteby-kan-inte-undersokas/</guid>\n"
	"      <link>https://www.expressen.se/nyheter/misstankt-foremal-i-otteby-kan-inte-undersokas/</link>\n"
	"      <author>alicia.heimersson@expressen.se (Alicia Heimersson)</author>\n"
	"      <title>Misstänkt föremål i Otteby – kan inte undersökas</title>\n"
	"      <description>\n"
	"        <![CDATA[<p>Boende uppmanas hålla sig undran</p>]]>\n"
	"      </description>\n"
	"      <pubDate>Fri, 24 Mar 2023 14:31:09 +0100</pubDate>\n"
	"      <isPremium>false</isPremium>\n"
	"    </item>\n"
	"    <item>\n"
	"      <guid isPermaLink=\"true\">https://www.expressen.se/nyheter/uppgifter-kriminalvarden-lat-kurdiske-raven-lamna-/</guid>\n"
	"      <link>https://www.expressen.se/nyheter/uppgifter-kriminalvarden-lat-kurdiske-raven-lamna-/</link>\n"
	"      <author>alicia.heimersson@expressen.se (Alicia Heimersson)</author>\n"
	"      <title>Uppgifter: Kriminalvården lät ”Kurdiske räven” lämna </title>\n"
	"      <description>\n"
	"        <![CDATA[<img src='https://static.cdn-expressen.se/images/7a/ca/7aca2d16fe65414f9ea4554e543f9525/16x9/265@70.jpg'/><p>Kriminalvården lät Rawa Majid, mer känd som ”Kurdiska räven”, att lämna Sverige.&nbsp;</p><p>Orsaken ska enligt SVT vara en akut hotbild mot den numera efterlyste 36-åringen.&nbsp;</p><p>– Det är ytterst ovanligt att vi har sådana här situationer, säger Henrik Svärd, frivårdschef på Kriminalvården, till <a href=\"https://www.svt.se/nyheter/lokalt/uppsala/kurdiske-raven-kriminalvarden-lat-utpekade-gangledaren-fly-sverige\">SVT</a>.&nbsp;</p>]]></description>\n"
	"      <pubDate>Fri, 24 Mar 2023 14:30:04 +0100</pubDate>\n"
	"      <isPremium>false</isPremium>\n"
	"    </item>\n"
	"    <item>\n"
	"      <guid isPermaLink=\"true\">https://www.expressen.se/nyheter/tvillingsystern-ida-kjos-sorg-efter-elin-kjos-dod/</guid>\n"
	"      <link>https://www.expressen.se/nyheter/tvillingsystern-ida-kjos-sorg-efter-elin-kjos-dod/</link>\n"
	"      <author>anna.friberg@expressen.se (Anna Friberg)</author>\n"
	"      <title>Tvillingsystern Ida Kjos sorg efter Elin Kjos död</title>\n"
	"      <description>\n"
	"        <![CDATA[<img src='https://static.cdn-expressen.se/images/d1/d7/d1d7bb557ca841cc9c28eb0277e8afd6/16x9/265@70.jpg'/><p>I onsdags kom beskedet att träningsprofilen Elin Kjos, 35, gått bort i cancer.&nbsp;</p><p>Nu berättar tvillingsystern Ida Kjos om sorgen.&nbsp;</p><p>”Ingen älskade mig som du. Och jag har aldrig älskat någon som jag älskat dig”, skriver hon på sitt <a href=\"https://www.instagram.com/p/CqKrh19MprK/?hl=sv\">Instagramkonto</a>.</p>]]></description>\n"
	"      <pubDate>Fri, 24 Mar 2023 14:17:26 +0100</pubDate>\n"
	"      <isPremium>false</isPremium>\n"
	"    </item>\n"
	"    <item>\n"
	"      <guid isPermaLink=\"true\">https://www.expressen.se/nyheter/brand-i-flerfamiljshus-ung-man-till-sjukhus/</guid>\n"
	"      <link>https://www.expressen.se/nyheter/brand-i-flerfamiljshus-ung-man-till-sjukhus/</link>\n"
	"      <author>alicia.heimersson@expressen.se (Alicia Heimersson)</author>\n"
	"      <title>Brand i flerfamiljshus – ung man till sjukhus</title>\n"
	"      <description>\n"
	"        <![CDATA[<img src='https://static.cdn-expressen.se/images/53/8d/538da8c9a25b426aaef007e84c4880eb/16x9/265@70.jpg'/><p>Under fredagen utbröt en brand på Hisingen i Göteborg.</p><p>Någon elektrisk apparat började brinna inne i ett sovrum i en lägenhet och en man i 25-årsåldern har fått föras till sjukhus med brännskador.</p><p>– Det var två grannar som lyckas ta sig in i den aktuella lägenheten och räddat den brandskadade mannen, säger Thomas Fuxborg, presstalesperson vid polisen i region väst.&nbsp;</p>]]></description>\n"
	"      <pubDate>Fri, 24 Mar 2023 13:49:26 +0100</pubDate>\n"
	"      <isPremium>false</isPremium>\n"
	"    </item>\n"
	"    <item>")

matches = re.search(regex, test_str)

if matches:
    #print ("Match was found at {start}-{end}: {match}".format(start = matches.start(), end = matches.end(), match = matches.group()))
    
    for groupNum in range(0, len(matches.groups())):
        groupNum = groupNum + 1
        
        print ("Group {groupNum} found at {start}-{end}: {group}".format(groupNum = groupNum, start = matches.start(groupNum), end = matches.end(groupNum), group = matches.group(groupNum)))

# Note: for Python 2.7 compatibility, use ur"" to prefix the regex and u"" to prefix the test string and substitution.
