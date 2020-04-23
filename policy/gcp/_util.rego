package rpe.gcp.util

projects_regex = ".*\/projects\/([a-z0-9-]{6,30})\/"

resource_from_collection_path(path, collection) = retval {
	prefix = concat("", ["/", collection, "/"])

	# Strip the first chunk off
	i := indexof(path, prefix)
	new_path := substring(path, i + count(prefix), -1)

	# Strip the remainder of the string if there are more path parts
	i2 := indexof(new_path, "/")
	retval := substring(new_path, 0, i2)
}
