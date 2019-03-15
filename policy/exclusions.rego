package exclusions

# A common list of valid values to be considered disabled
_disable = ["disable", "disabled", "off", "no", "0"]

# A list of labels and possible values that we should exclude
labels = {
  "forseti-enforcer": _disable,
}

# Function to test if a resource label is present that marks the resource for exclusion
label_exclude(res_labels) = result {
  # Do we have a matching label name?
  res_labels[key]
  labels[key]

  # Does the label's value also match
  labels[key][_] = value
  result = (res_labels[key] == value)
}
