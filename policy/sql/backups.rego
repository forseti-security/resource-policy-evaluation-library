package gcp.sqladmin.instances.policy.backups

default valid=false

valid = true {
  input.settings.backupConfiguration.enabled == true
}

remediate[key] = value {
 key != "settings"
 input[key]=value
}

remediate[key] = value {
 key := "settings"
 value := _settings
}

_settings[key]=value{
  key != "backupConfiguration"
  input.settings[key]=value
}

_settings[key]=value{
  key := "backupConfiguration"
  value := _backupConfiguration
}

_backupConfiguration[key] = value {
  key != "enabled"
  input.settings.backupConfiguration[key] = value
}

_backupConfiguration[key] = value {
  key := "enabled"
  value := true
}
