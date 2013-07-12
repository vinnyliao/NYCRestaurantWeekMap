#!/usr/bin/python

from sys import argv
from urllib.request import urlopen
from bs4 import BeautifulSoup
from re import search

if len(argv) != 2:
	print("usage: python3 tsvgen.py <output_file>")
else:
	# get the HTML source of http://www.nycgo.com/restaurantweek
	str_nycgo = urlopen("http://www.nycgo.com/restaurantweek").read().decode("iso-8859-1")
	str_nycgo = str_nycgo.replace("\"The Original\"", "\'The Original\'")	# replace one particular instance of troublesome double quotes so BeautifulSoup can work

	# generate a soup for http://www.nycgo.com/restaurantweek
	soup_nycgo = BeautifulSoup(str_nycgo)

	# get the HTML source of http://www.opentable.com/new-york-restaurant-listings
	str_ot = urlopen("http://www.opentable.com/new-york-restaurant-listings").read().decode("utf-8")

	# BeautifulSoup unfortunately does not work for http://www.opentable.com/new-york-restaurant-listings so we have to use regex later

	# open the output file
	file_out = open(argv[1], 'w')

	# write the columns
	#file_out.write("Latitude\t")
	#file_out.write("Longitude\t")
	file_out.write("Name\t")
	file_out.write("Cuisine\t")
	file_out.write("Menu\t")
	file_out.write("Meals\t")
	file_out.write("Lunch\t")
	file_out.write("Dinner\t")
	file_out.write("Address\t")
	file_out.write("Phone\t")
	file_out.write("Website\t")
	file_out.write("Price\t")
	file_out.write("Rating\t")
	file_out.write("Reserve")

	restaurant_count = 0	# keep a count of the number of restaurants processed
	warnings = []			# keep track of warnings

	# iterate through restaurants (each <tr> in <tbody> in the nycgo.com source corresponds to a restaurant)
	for restaurant in soup_nycgo.find("tbody").findAll("tr"):
		# list of <td> tags in the current <tr>, from which we will get info
		tds = restaurant.findAll("td")

		# get name, url, and menu from the 1st <td>
		name = tds[0].find("a").string.strip()
		url = "http://www.nycgo.com" + tds[0].find("a")["href"].strip()
		nycgo_id = search(r"/venues/(?P<nycgo_id>[^/]*)/", url).group("nycgo_id").strip()	# used to get the menu url
		menu = "<a href=\"http://www.nycgo.com/assets/files/programs/rw/2012W/" + nycgo_id + ".pdf\" target=\"_blank\">View PDF</a>" if tds[0].find("a", "rwMenuLink") else "not available"

		# get cuisine from the 2nd <td>
		cuisine = tds[1].string.strip()

		# get meals, lunch, and dinner from the 3rd <td>
		meals = tds[2].string.strip().title().replace(",", " and")
		lunch = "yes" if "lunch" in tds[2].string else "no"
		dinner = "yes" if "dinner" in tds[2].string else "no"

		# get neighborhood from the 3rd <td>
		neighborhood = tds[3].string.strip()

		# get reserve link from the 4th <td>
		reserve = "<a href=\"http://www.nycgo.com" + tds[4].find("a")["href"].strip() + "\">Book Now</a>"
		r = search(r"/ot/(?P<ot_id>[^/]*)", reserve)
		ot_id = r.group("ot_id") if r != None else None
		if r == None: reserve = "not available"

		# get the HTML source of the restaurant's nycgo.com venue page
		str_venue = urlopen(url).read().decode("utf-8")

		# generate a soup for the restaurant's nycgo.com venue page
		soup_venue = BeautifulSoup(str_venue)

		# the first <ul class="geoResults"> in the venue page should correspond to the restaurant
		georesults = soup_venue.find("ul", "geoResults")

		# record a warning if the restaurant has no <ul class="geoResults">
		if georesults == None: warnings.append(name + " has no georesults")
		
		# get address, latitude, and longitude from the <ul class="geoResults">
		address = georesults.find("span", "address").string if georesults != None else ""
		latitude = georesults.find("abbr", "latitude")["title"] if georesults != None else ""
		longitude = georesults.find("abbr", "longitude")["title"] if georesults != None else ""

		# the restaurant's address is also contained in the only <h6> tags on the page
		h6s = soup_venue.findAll("h6")
		alt_address = ""
		for h6 in h6s: alt_address += h6.string + ", "
		alt_address = alt_address.rstrip(", ")

		# record warnings if there is no alternate address or if the address and alternate address differ in the first 5 characters
		if alt_address == "": warnings.append(name + " has no address")
		elif address != "" and address[:5] != alt_address[:5]: warnings.append(name + " may have the wrong address")

		# <ul class="genInfo"> should contain the restaurant's price, phone, and website
		geninfo = str(soup_venue.find("ul", "genInfo"))

		# get price from <ul class="genInfo">
		r = search(r"price:</strong>(?P<price>[^<>]*)", geninfo)
		price = r.group("price") if r != None else ""

		# get phone from <ul class="genInfo">
		r = search(r"phone:</strong>(?P<phone>[^<>]*)", geninfo)
		phone = r.group("phone") if r != None else ""

		# get website from <ul class="genInfo">
		r = search(r"website:</strong>\s*(?P<website>[^>]*>[^<]*</a>)", geninfo)
		website = r.group("website") if r != None else ""

		# record warnings if there is no price, phone, or website
		if price == "": warnings.append(name + " has no price")
		if phone == "": warnings.append(name + " has no phone")
		if website == "": warnings.append(name + " has no website")

		# get the rating and ot_price from the OpenTabl.com source
		rating = "0"
		ot_price = ""
		if ot_id != None:
			r = search(r"rid=\"%s\".*\"RaCol\".*?((?P<rating>[\d\.]*) stars.*)?\"PrCol\">(?P<price>[$]*)" % ot_id, str_ot)
			if r != None:
				ot_price = r.group('price')
				if r.group('rating'):
					rating = r.group('rating')
		
		if rating == "": warnings.append(name + " has no rating")

		# output values to the terminal
		print("name: " + name)
		print("url: " + url)
		print("menu: " + menu)
		print("cuisine: " + cuisine)
		print("meals: " + meals)
		print("lunch: " + lunch)
		print("dinner: " + dinner)
		print("neighborhood: " + neighborhood)
		print("reserve: " + reserve)
		print("address: " + address)
		print("alt_address: " + alt_address)
		print("latitude: " + latitude)
		print("longitude: " + longitude)
		print("price: " + price)
		print("ot price: " + ot_price)
		print("rating: " + rating)
		print("phone: " + phone)
		print("website: " + website)
		print("---")

		# substitute the alternate address for address if necessary
		if address == "":
			address = alt_address
			warnings.append("using alternate address for " + name)

		# substitute the Open Table price for price if necessary
		if price == "":
			price = ot_price
			warnings.append("using alternate price for " + name)

		# write a row for the current restaurant
		#file_out.write("\n%s" % latitude)
		#file_out.write("\t%s" % longitude)
		file_out.write("\n%s" % name)
		file_out.write("\t%s" % cuisine)
		file_out.write("\t%s" % menu)
		file_out.write("\t%s" % meals)
		file_out.write("\t%s" % lunch)
		file_out.write("\t%s" % dinner)
		file_out.write("\t%s" % address)
		file_out.write("\t%s" % phone)
		file_out.write("\t%s" % website)
		file_out.write("\t%s" % price)
		file_out.write("\t%s" % rating)
		file_out.write("\t%s" % reserve)

		# increment the number of restaurants processed
		restaurant_count += 1
	
	print("number of restaurants processed: " + str(restaurant_count))
	for p in warnings:
		print(p)