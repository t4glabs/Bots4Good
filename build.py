#!/bin/python

# Toolkit build script: https://toolkit.t4glabs.org

from collections import OrderedDict
import shutil
import os
import yaml
from jinja2 import Template


def load_data(file):
	with open(file, "r") as f:
		out = yaml.load(f.read(), Loader=yaml.FullLoader)
		for item in out:
			item["filters"].sort()
			item["tags"].sort()
		#print(out)
		return out


# Returns the list of unique tags from across all entries in the data.
def get_tags(data):
	tags = {}
	for d in data:
		for t in d["tags"]:
			if t not in tags:
				tags[t] = 0
			tags[t] += 1
	#print(tags)
	return OrderedDict(sorted(tags.items()))


# Returns the list of unique categories from across all entries in the data.
def get_categories(data):
	cat = {}
	for d in data:
		for c in d["categories"]:
			if c not in cat:
				cat[c] = 0
			cat[c] += 1
	#print(OrderedDict(sorted(cat.items())))
	return OrderedDict(sorted(cat.items()))


def get_filters(data):
	filter = {}
	for d in data:
		for l in d["filters"]:
			if l not in filter:
				filter[l] = 0
			filter[l] += 1

	return OrderedDict(sorted(filter.items()))


def filter_by_category(category, data):
	#print(sorted([d for d in data if category in d["categories"]], key=lambda k: k["name"].lower()))
	return sorted([d for d in data if category in d["categories"]], key=lambda k: k["name"].lower())


def load_template(file):
	with open(file, "r") as f:
		return Template(f.read())


def make_filename(file, out_dir):
	for i in range(0, len(file), 1):
		# Changing the ith character
        # to '-' if it's a space.
		if (file[i] == ' '):
			file = file.replace(file[i], '-')

	return "{}/{}.html".format(out_dir, file.lower())


def render_page(category, data, tpl, file):
	cats = get_categories(data)
	items = filter_by_category(category, data)
	list_filter = get_filters(items)
	list_tags = get_tags(items)

	html = tpl.render(categories=cats,
		category=category,
		list_filters=list_filter,
		list_tags=list_tags,
		list=items)

	with open(file, "w", encoding="utf-8") as f:
		f.write(html)


def render_all(data, tpl, out_dir):
	tags = get_tags(data)
	cat = get_categories(data)

	for c in cat:
		render_page(c, data, tpl, make_filename(c, out_dir))


if __name__ == "__main__":
	out_dir = "site"
	to_copy = ["static"]
	tpl_file = "template.html"
	data_file = "data.yml"

	# Clear the output directory.
	if os.path.exists(out_dir):
		shutil.rmtree(out_dir)

	# Re-create the output directory.
	os.mkdir(out_dir)

	# Copy the static directory into the output directory.
	for f in to_copy:
		target = os.path.join(out_dir, f)
		if os.path.isfile(f):
			shutil.copyfile(f, target)
		else:
			shutil.copytree(f, target)

	# Load the data and template.
	tpl = load_template(tpl_file)
	data = load_data(data_file)

  # Generate all pages.
	render_all(data, tpl, out_dir)

	# The first category alphabetically, generate it as index.html
	cat = next(iter(get_categories(data)))
	render_page(cat, data, tpl, make_filename("index", out_dir))
