# Flagdays
This is a HomeAssistant component for tracking flagdays, where the state of each flagday is equal to how many days are left. All flagdays are updated at midnight.

## Installation

### HACS (recommended)
1. Go to integrations
2. Press the dotted menu in the top right corner
3. Choose custom repositories
4. Add the URL to this repository
5. Choose category `Integration`
6. Click add

### Manual
1. In your homeassistant config directory, create a new directory. The path should look like this: **my-ha-config-dir/custom_components
2. Copy the contents of /custom_components in this git-repo to your newly created directory in HA

## Set up
Set up the component:
~~~~
# Example configuration.yaml entry
flagdays:
  - name: '1. nyttårsdag'
    date_of_flag: 01-01
  - name: 'Grunnlovsdagen'
    date_of_flag: 05-17
  - name: 'Frigjøringsdagen 1945'
    date_of_flag: 05-08
    icon: 'mdi:flag'
~~~~
Restart homeassistant

## Entities
All entities are exposed using the format `flagdays.{name}`. Any character that does not fit the pattern `a-z`, `A-Z`, `0-9`, or `_` will be changed. For instance `Frigjøringsdagen 1945` will get entity_id `frigjøringsdagen_1945`.

## Automation
All flagdays are updated at midnight, and when a flagday occurs an event is sent on the HA bus that can be used for automations. The event is called `flagday` and contains the data `name`.

Sending a push notification for each flagday (with PushBullet) looks like this:
~~~
automation:
  trigger:
    platform: event
    event_type: 'flagday'
    action:
      service: notify.pushbullet
      data_template:
        title: 'Flagday!'
        message: "Today is flagday for {{ trigger.event.data.name }}"
~~~

If you want to trigger an automation based on a specific name or age, you can use the following:
~~~
automation:
  trigger:
    platform: event
    event_type: 'flagday'
    event_data:
      name: frigjøringsdagen_1945
    action:
      service: notify.pushbullet
      data_template:
        title: 'Flagday!'
        message: "Today is flagday for {{ trigger.event.data.name }}"
~~~

## Lovelace UI
I use the birthdays as a simple entity list in lovelace, given the above example I use:
~~~
# Example use in lovelace
- type: entities
  title: Flagdays
  show_header_toggle: false
  entities:
    - flagdays.frigjøringsdagen_1945
~~~
