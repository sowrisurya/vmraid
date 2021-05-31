// VMRaid Chat
// Author - Achilles Rasquinha <achilles@vmraid.io>

import Fuse   from 'fuse.js'
import hyper  from '../lib/hyper.min'

import './socketio_client'

import './ui/dialog'
import './ui/capture'

import './utils/user'

/* eslint semi: "never" */
// Fuck semicolons - https://mislav.net/2010/05/semicolons

// vmraid extensions

/**
 * @description The base class for all VMRaid Errors.
 *
 * @example
 * try
 *      throw new vmraid.Error("foobar")
 * catch (e)
 *      console.log(e.name)
 * // returns "VMRaidError"
 *
 * @see  https://stackoverflow.com/a/32749533
 * @todo Requires "transform-builtin-extend" for Babel 6
 */
vmraid.Error = Error
// class extends Error {
// 	constructor (message) {
// 		super (message)

// 		this.name = 'VMRaidError'

// 		if ( typeof Error.captureStackTrace === 'function' )
// 			Error.captureStackTrace(this, this.constructor)
// 		else
// 			this.stack = (new Error(message)).stack
// 	}
// }

/**
 * @description TypeError
 */
vmraid.TypeError  = TypeError
// class extends vmraid.Error {
// 	constructor (message) {
// 		super (message)

// 		this.name = this.constructor.name
// 	}
// }

/**
 * @description ValueError
 */
vmraid.ValueError = Error
// class extends vmraid.Error {
// 	constructor (message) {
// 		super (message)

// 		this.name = this.constructor.name
// 	}
// }

/**
 * @description ImportError
 */
vmraid.ImportError = Error
// class extends vmraid.Error {
// 	constructor (message) {
// 		super (message)

// 		this.name  = this.constructor.name
// 	}
// }

// vmraid.datetime
vmraid.provide('vmraid.datetime')

/**
 * @description VMRaid's datetime object. (Inspired by Python's datetime object).
 *
 * @example
 * const datetime = new vmraid.datetime.datetime()
 */
vmraid.datetime.datetime = class {
	/**
	 * @description VMRaid's datetime Class's constructor.
	 */
	constructor (instance, format = null) {
		if ( typeof moment === 'undefined' )
			throw new vmraid.ImportError(`Moment.js not installed.`)

		this.moment = instance ? moment(instance, format) : moment()
	}

	/**
	 * @description Returns a formatted string of the datetime object.
	 */
	format (format = null) {
		const  formatted = this.moment.format(format)
		return formatted
	}
}

/**
 * @description VMRaid's daterange object.
 *
 * @example
 * const range = new vmraid.datetime.range(vmraid.datetime.now(), vmraid.datetime.now())
 * range.contains(vmraid.datetime.now())
 */
vmraid.datetime.range   = class {
	constructor (start, end) {
		if ( typeof moment === undefined )
			throw new vmraid.ImportError(`Moment.js not installed.`)

		this.start = start
		this.end   = end
	}

	contains (datetime) {
		const  contains = datetime.moment.isBetween(this.start.moment, this.end.moment)
		return contains
	}
}

/**
 * @description Returns the current datetime.
 *
 * @example
 * const datetime = new vmraid.datetime.now()
 */
vmraid.datetime.now   = () => new vmraid.datetime.datetime()

vmraid.datetime.equal = (a, b, type) => {
	a = a.moment
	b = b.moment

	const equal = a.isSame(b, type)

	return equal
}

/**
 * @description Compares two vmraid.datetime.datetime objects.
 *
 * @param   {vmraid.datetime.datetime} a - A vmraid.datetime.datetime/moment object.
 * @param   {vmraid.datetime.datetime} b - A vmraid.datetime.datetime/moment object.
 *
 * @returns {number} 0 (if a and b are equal), 1 (if a is before b), -1 (if a is after b).
 *
 * @example
 * vmraid.datetime.compare(vmraid.datetime.now(), vmraid.datetime.now())
 * // returns 0
 * const then = vmraid.datetime.now()
 *
 * vmraid.datetime.compare(then, vmraid.datetime.now())
 * // returns 1
 */
vmraid.datetime.compare = (a, b) => {
	a = a.moment
	b = b.moment

	if ( a.isBefore(b) )
		return  1
	else
	if ( b.isBefore(a) )
		return -1
	else
		return  0
}

// vmraid.quick_edit
vmraid.quick_edit      = (doctype, docname, fn) => {
	return new Promise(resolve => {
		vmraid.model.with_doctype(doctype, () => {
			vmraid.db.get_doc(doctype, docname).then(doc  => {
				const meta     = vmraid.get_meta(doctype)
				const fields   = meta.fields
				const required = fields.filter(f => f.reqd || f.bold && !f.read_only)

				required.map(f => {
					if(f.fieldname == 'content' && doc.type == 'File') {
						f['read_only'] = 1;
					}
				})

				const dialog   = new vmraid.ui.Dialog({
					title: __('Edit') + `${doctype} (${docname})`,
					fields: required,
					action: {
						primary: {
							   label: __("Save"),
							onsubmit: (values) => {
								vmraid.call('vmraid.client.save',
									{ doc: { doctype: doctype, docname: docname, ...doc, ...values } })
									  .then(r => {
										if ( fn )
											fn(r.message)

										resolve(r.message)
									  })

								dialog.hide()
							}
						},
						secondary: {
							label: __("Discard")
						}
					}
				})
				dialog.set_values(doc)

				const $element = $(dialog.body)
				$element.append(`
					<div class="qe-fp" style="padding-top: '15px'; padding-bottom: '15px'; padding-left: '7px'">
						<button class="btn btn-default btn-sm">
							${__("Edit in Full Page")}
						</button>
					</div>
				`)
				$element.find('.qe-fp').click(() => {
					dialog.hide()
					vmraid.set_route('Form', doctype, docname)
				})

				dialog.show()
			})
		})
	})
}

// vmraid._
// vmraid's utility namespace.
vmraid.provide('vmraid._')

// String Utilities

/**
 * @description Python-inspired format extension for string objects.
 *
 * @param  {string} string - A string with placeholders.
 * @param  {object} object - An object with placeholder, value pairs.
 *
 * @return {string}        - The formatted string.
 *
 * @example
 * vmraid._.format('{foo} {bar}', { bar: 'foo', foo: 'bar' })
 * // returns "bar foo"
 */
vmraid._.format = (string, object) => {
	for (const key in object)
		string  = string.replace(`{${key}}`, object[key])

	return string
}

/**
 * @description Fuzzy Search a given query within a dataset.
 *
 * @param  {string} query   - A query string.
 * @param  {array}  dataset - A dataset to search within, can contain singletons or objects.
 * @param  {object} options - Options as per fuze.js
 *
 * @return {array}          - The fuzzy matched index/object within the dataset.
 *
 * @example
 * vmraid._.fuzzy_search("foobar", ["foobar", "bartender"])
 * // returns [0, 1]
 *
 * @see http://fusejs.io
 */
vmraid._.fuzzy_search = (query, dataset, options) => {
	const DEFAULT     = {
				shouldSort: true,
				 threshold: 0.6,
				  location: 0,
				  distance: 100,
		minMatchCharLength: 1,
		  maxPatternLength: 32
	}
	options       = { ...DEFAULT, ...options }

	const fuse    = new Fuse(dataset, options)
	const result  = fuse.search(query)

	return result
}

/**
 * @description Pluralizes a given word.
 *
 * @param  {string} word  - The word to be pluralized.
 * @param  {number} count - The count.
 *
 * @return {string}       - The pluralized string.
 *
 * @example
 * vmraid._.pluralize('member',  1)
 * // returns "member"
 * vmraid._.pluralize('members', 0)
 * // returns "members"
 *
 * @todo Handle more edge cases.
 */
vmraid._.pluralize = (word, count = 0, suffix = 's') => `${word}${count === 1 ? '' : suffix}`

/**
 * @description Captializes a given string.
 *
 * @param   {word}  - The word to be capitalized.
 *
 * @return {string} - The capitalized word.
 *
 * @example
 * vmraid._.capitalize('foobar')
 * // returns "Foobar"
 */
vmraid._.capitalize = word => `${word.charAt(0).toUpperCase()}${word.slice(1)}`

// Array Utilities

/**
 * @description Returns the first element of an array.
 *
 * @param   {array} array - The array.
 *
 * @returns - The first element of an array, undefined elsewise.
 *
 * @example
 * vmraid._.head([1, 2, 3])
 * // returns 1
 * vmraid._.head([])
 * // returns undefined
 */
vmraid._.head = arr => vmraid._.is_empty(arr) ? undefined : arr[0]

/**
 * @description Returns a copy of the given array (shallow).
 *
 * @param   {array} array - The array to be copied.
 *
 * @returns {array}       - The copied array.
 *
 * @example
 * vmraid._.copy_array(["foobar", "barfoo"])
 * // returns ["foobar", "barfoo"]
 *
 * @todo Add optional deep copy.
 */
vmraid._.copy_array = array => {
	if ( Array.isArray(array) )
		return array.slice()
	else
		throw vmraid.TypeError(`Expected Array, recieved ${typeof array} instead.`)
}

/**
 * @description Check whether an array|string|object|jQuery is empty.
 *
 * @param   {any}     value - The value to be checked on.
 *
 * @returns {boolean}       - Returns if the object is empty.
 *
 * @example
 * vmraid._.is_empty([])      // returns true
 * vmraid._.is_empty(["foo"]) // returns false
 *
 * vmraid._.is_empty("")      // returns true
 * vmraid._.is_empty("foo")   // returns false
 *
 * vmraid._.is_empty({ })            // returns true
 * vmraid._.is_empty({ foo: "bar" }) // returns false
 *
 * vmraid._.is_empty($('.papito'))   // returns false
 *
 * @todo Handle other cases.
 */
vmraid._.is_empty = value => {
	let empty = false

	if ( value === undefined || value === null )
		empty = true
	else
	if ( Array.isArray(value) || typeof value === 'string' || value instanceof $ )
		empty = value.length === 0
	else
	if ( typeof value === 'object' )
		empty = Object.keys(value).length === 0

	return empty
}

/**
 * @description Converts a singleton to an array, if required.
 *
 * @param {object} item - An object
 *
 * @example
 * vmraid._.as_array("foo")
 * // returns ["foo"]
 *
 * vmraid._.as_array(["foo"])
 * // returns ["foo"]
 *
 * @see https://docs.oracle.com/javase/8/docs/api/java/util/Arrays.html#asList-T...-
 */
vmraid._.as_array = item => Array.isArray(item) ? item : [item]

/**
 * @description Return a singleton if array contains a single element.
 *
 * @param   {array}        list - An array to squash.
 *
 * @returns {array|object}      - Returns an array if there's more than 1 object else the first object itself.
 *
 * @example
 * vmraid._.squash(["foo"])
 * // returns "foo"
 *
 * vmraid._.squash(["foo", "bar"])
 * // returns ["foo", "bar"]
 */
vmraid._.squash = list => Array.isArray(list) && list.length === 1 ? list[0] : list

/**
 * @description Returns true, if the current device is a mobile device.
 *
 * @example
 * vmraid._.is_mobile()
 * // returns true|false
 *
 * @see https://developer.mozilla.org/en-US/docs/Web/HTTP/Browser_detection_using_the_user_agent
 */
vmraid._.is_mobile = () => {
	const regex    = new RegExp("Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini", "i")
	const agent    = navigator.userAgent
	const mobile   = regex.test(agent)

	return mobile
}

/**
 * @description Removes falsey values from an array.
 *
 * @example
 * vmraid._.compact([1, 2, false, NaN, ''])
 * // returns [1, 2]
 */
vmraid._.compact   = array => array.filter(Boolean)

// extend utils to base.
vmraid.utils       = { ...vmraid.utils, ...vmraid._ }

// vmraid extensions

// vmraid.user extensions
/**
 * @description Returns the first name of a User.
 *
 * @param {string} user - User
 *
 * @returns The first name of the user.
 *
 * @example
 * vmraid.user.first_name("Rahul Malhotra")
 * // returns "Rahul"
 */
vmraid.provide('vmraid.user')
vmraid.user.first_name = user => vmraid._.head(vmraid.user.full_name(user).split(" "))

vmraid.provide('vmraid.ui.keycode')
vmraid.ui.keycode = { RETURN: 13 }

/**
 * @description VMRaid's Store Class
 */
 // vmraid.stores  - A registry for vmraid stores.
vmraid.provide('vmraid.stores')
vmraid.stores = [ ]
vmraid.Store  = class
{
	/**
	 * @description VMRaid's Store Class's constructor.
	 *
	 * @param {string} name - Name of the logger.
	 */
	constructor (name) {
		if ( typeof name !== 'string' )
			throw new vmraid.TypeError(`Expected string for name, got ${typeof name} instead.`)
		this.name = name
	}

	/**
	 * @description Get instance of vmraid.Store (return registered one if declared).
	 *
	 * @param {string} name - Name of the store.
	 */
	static get (name) {
		if ( !(name in vmraid.stores) )
			vmraid.stores[name] = new vmraid.Store(name)
		return vmraid.stores[name]
	}

	set (key, value) { localStorage.setItem(`${this.name}:${key}`, value) }
	get (key, value) { return localStorage.getItem(`${this.name}:${key}`) }
}

// vmraid.loggers - A registry for vmraid loggers.
vmraid.provide('vmraid.loggers')
/**
 * @description VMRaid's Logger Class
 *
 * @example
 * vmraid.log       = vmraid.Logger.get('foobar')
 * vmraid.log.level = vmraid.Logger.DEBUG
 *
 * vmraid.log.info('foobar')
 * // prints '[timestamp] foobar: foobar'
 */
vmraid.Logger = class {
	/**
	 * @description VMRaid's Logger Class's constructor.
	 *
	 * @param {string} name - Name of the logger.
	 */
	constructor (name, level) {
		if ( typeof name !== 'string' )
			throw new vmraid.TypeError(`Expected string for name, got ${typeof name} instead.`)

		this.name   = name
		this.level  = level

		if ( !this.level ) {
			if ( vmraid.boot.developer_mode )
				this.level = vmraid.Logger.ERROR
			else
				this.level = vmraid.Logger.NOTSET
		}
		this.format = vmraid.Logger.FORMAT
	}

	/**
	 * @description Get instance of vmraid.Logger (return registered one if declared).
	 *
	 * @param {string} name - Name of the logger.
	 */
	static get (name, level) {
		if ( !(name in vmraid.loggers) )
			vmraid.loggers[name] = new vmraid.Logger(name, level)
		return vmraid.loggers[name]
	}

	debug (message) { this.log(message, vmraid.Logger.DEBUG) }
	info  (message) { this.log(message, vmraid.Logger.INFO)  }
	warn  (message) { this.log(message, vmraid.Logger.WARN)  }
	error (message) { this.log(message, vmraid.Logger.ERROR) }

	log (message, level) {
		const timestamp   = vmraid.datetime.now()

		if ( level.value <= this.level.value ) {
			const format  = vmraid._.format(this.format, {
				time: timestamp.format('HH:mm:ss'),
				name: this.name
			})
			console.log(`%c ${format}:`, `color: ${level.color}`, message)
		}
	}
}

vmraid.Logger.DEBUG  = { value: 10, color: '#616161', name: 'DEBUG'  }
vmraid.Logger.INFO   = { value: 20, color: '#2196F3', name: 'INFO'   }
vmraid.Logger.WARN   = { value: 30, color: '#FFC107', name: 'WARN'   }
vmraid.Logger.ERROR  = { value: 40, color: '#F44336', name: 'ERROR'  }
vmraid.Logger.NOTSET = { value:  0,                   name: 'NOTSET' }

vmraid.Logger.FORMAT = '{time} {name}'

// vmraid.chat
vmraid.provide('vmraid.chat')

vmraid.log = vmraid.Logger.get('vmraid.chat', vmraid.Logger.NOTSET)

// vmraid.chat.profile
vmraid.provide('vmraid.chat.profile')

/**
 * @description Create a Chat Profile.
 *
 * @param   {string|array} fields - (Optional) fields to be retrieved after creating a Chat Profile.
 * @param   {function}     fn     - (Optional) callback with the returned Chat Profile.
 *
 * @returns {Promise}
 *
 * @example
 * vmraid.chat.profile.create(console.log)
 *
 * vmraid.chat.profile.create("status").then(console.log) // { status: "Online" }
 */
vmraid.chat.profile.create = (fields, fn) => {
	if ( typeof fields === "function" ) {
		fn     = fields
		fields = null
	} else
	if ( typeof fields === "string" )
		fields = vmraid._.as_array(fields)

	return new Promise(resolve => {
		vmraid.call("vmraid.chat.doctype.chat_profile.chat_profile.create",
			{ user: vmraid.session.user, exists_ok: true, fields: fields },
				response => {
					if ( fn )
						fn(response.message)

					resolve(response.message)
				})
	})
}

/**
 * @description Updates a Chat Profile.
 *
 * @param   {string} user   - (Optional) Chat Profile User, defaults to session user.
 * @param   {object} update - (Required) Updates to be dispatched.
 *
 * @example
 * vmraid.chat.profile.update(vmraid.session.user, { "status": "Offline" })
 */
vmraid.chat.profile.update = (user, update, fn) => {
	return new Promise(resolve => {
		vmraid.call("vmraid.chat.doctype.chat_profile.chat_profile.update",
			{ user: user || vmraid.session.user, data: update },
				response => {
					if ( fn )
						fn(response.message)

					resolve(response.message)
				})
	})
}

// vmraid.chat.profile.on
vmraid.provide('vmraid.chat.profile.on')

/**
 * @description Triggers on a Chat Profile update of a user (Only if there's a one-on-one conversation).
 *
 * @param   {function} fn - (Optional) callback with the User and the Chat Profile update.
 *
 * @returns {Promise}
 *
 * @example
 * vmraid.chat.profile.on.update(function (user, update)
 * {
 *      // do stuff
 * })
 */
vmraid.chat.profile.on.update = function (fn) {
	vmraid.realtime.on("vmraid.chat.profile:update", r => fn(r.user, r.data))
}
vmraid.chat.profile.STATUSES
=
[
	{
		name: "Online",
	   color: "green"
	},
	{
		 name: "Away",
		color: "yellow"
	},
	{
		 name: "Busy",
		color: "red"
	},
	{
		 name: "Offline",
		color: "gray"
	}
]

// vmraid.chat.room
vmraid.provide('vmraid.chat.room')

/**
 * @description Creates a Chat Room.
 *
 * @param   {string}       kind  - (Required) "Direct", "Group" or "Visitor".
 * @param   {string}       owner - (Optional) Chat Room owner (defaults to current user).
 * @param   {string|array} users - (Required for "Direct" and "Visitor", Optional for "Group") User(s) within Chat Room.
 * @param   {string}       name  - Chat Room name.
 * @param   {function}     fn    - callback with created Chat Room.
 *
 * @returns {Promise}
 *
 * @example
 * vmraid.chat.room.create("Direct", vmraid.session.user, "foo@bar.com", function (room) {
 *      // do stuff
 * })
 * vmraid.chat.room.create("Group",  vmraid.session.user, ["santa@gmail.com", "banta@gmail.com"], "Santa and Banta", function (room) {
 *      // do stuff
 * })
 */
vmraid.chat.room.create = function (kind, owner, users, name, fn) {
	if ( typeof name === "function" ) {
		fn   = name
		name = null
	}

	users    = vmraid._.as_array(users)

	return new Promise(resolve => {
		vmraid.call("vmraid.chat.doctype.chat_room.chat_room.create",
			{ kind: kind, token: owner || vmraid.session.user, users: users, name: name },
			r => {
				let room = r.message
				room     = { ...room, creation: new vmraid.datetime.datetime(room.creation) }

				if ( fn )
					fn(room)

				resolve(room)
			})
	})
}

/**
 * @description Returns Chat Room(s).
 *
 * @param   {string|array} names   - (Optional) Chat Room(s) to retrieve.
 * @param   {string|array} fields  - (Optional) fields to be retrieved for each Chat Room.
 * @param   {function}     fn      - (Optional) callback with the returned Chat Room(s).
 *
 * @returns {Promise}
 *
 * @example
 * vmraid.chat.room.get(function (rooms) {
 *      // do stuff
 * })
 * vmraid.chat.room.get().then(function (rooms) {
 *      // do stuff
 * })
 *
 * vmraid.chat.room.get(null, ["room_name", "avatar"], function (rooms) {
 *      // do stuff
 * })
 *
 * vmraid.chat.room.get("CR00001", "room_name", function (room) {
 *      // do stuff
 * })
 *
 * vmraid.chat.room.get(["CR00001", "CR00002"], ["room_name", "last_message"], function (rooms) {
 *
 * })
 */
vmraid.chat.room.get = function (names, fields, fn) {
	if ( typeof names === "function" ) {
		fn     = names
		names  = null
		fields = null
	}
	else
	if ( typeof names === "string" ) {
		names  = vmraid._.as_array(names)

		if ( typeof fields === "function" ) {
			fn     = fields
			fields = null
		}
		else
		if ( typeof fields === "string" )
			fields = vmraid._.as_array(fields)
	}

	return new Promise(resolve => {
		vmraid.call("vmraid.chat.doctype.chat_room.chat_room.get",
			{ user: vmraid.session.user, rooms: names, fields: fields },
				response => {
					let rooms = response.message
					if ( rooms ) { // vmraid.api BOGZ! (emtpy arrays are falsified, not good design).
						rooms = vmraid._.as_array(rooms)
						rooms = rooms.map(room => {
							return { ...room, creation: new vmraid.datetime.datetime(room.creation),
								last_message: room.last_message ? {
									...room.last_message,
									creation: new vmraid.datetime.datetime(room.last_message.creation)
								} : null
							}
						})
						rooms = vmraid._.squash(rooms)
					}
					else
						rooms = [ ]

					if ( fn )
						fn(rooms)

					resolve(rooms)
				})
	})
}

/**
 * @description Subscribe current user to said Chat Room(s).
 *
 * @param {string|array} rooms - Chat Room(s).
 *
 * @example
 * vmraid.chat.room.subscribe("CR00001")
 */
vmraid.chat.room.subscribe = function (rooms) {
	vmraid.realtime.publish("vmraid.chat.room:subscribe", rooms)
}

/**
 * @description Get Chat Room history.
 *
 * @param   {string} name - Chat Room name
 *
 * @returns {Promise}     - Chat Message(s)
 *
 * @example
 * vmraid.chat.room.history(function (messages)
 * {
 *      // do stuff.
 * })
 */
vmraid.chat.room.history = function (name, fn) {
	return new Promise(resolve => {
		vmraid.call("vmraid.chat.doctype.chat_room.chat_room.history",
			{ room: name, user: vmraid.session.user },
				r => {
					let messages = r.message ? vmraid._.as_array(r.message) : [ ] // vmraid.api BOGZ! (emtpy arrays are falsified, not good design).
					messages     = messages.map(m => {
						return { ...m,
							creation: new vmraid.datetime.datetime(m.creation)
						}
					})

					if ( fn )
						fn(messages)

					resolve(messages)
				})
	})
}

/**
 * @description Searches Rooms based on a query.
 *
 * @param   {string} query - The query string.
 * @param   {array}  rooms - A list of Chat Rooms.
 *
 * @returns {array}        - A fuzzy searched list of rooms.
 */
vmraid.chat.room.search = function (query, rooms) {
	const dataset = rooms.map(r => {
		if ( r.room_name )
			return r.room_name
		else
			if ( r.owner === vmraid.session.user )
				return vmraid.user.full_name(vmraid._.squash(r.users))
			else
				return vmraid.user.full_name(r.owner)
	})
	const results = vmraid._.fuzzy_search(query, dataset)
	rooms         = results.map(i => rooms[i])

	return rooms
}

/**
 * @description Sort Chat Room(s) based on Last Message Timestamp or Creation Date.
 *
 * @param {array}   - A list of Chat Room(s)
 * @param {compare} - (Optional) a comparision function.
 */
vmraid.chat.room.sort = function (rooms, compare = null) {
	compare = compare || function (a, b) {
		if ( a.last_message && b.last_message )
			return vmraid.datetime.compare(a.last_message.creation, b.last_message.creation)
		else
		if ( a.last_message )
			return vmraid.datetime.compare(a.last_message.creation, b.creation)
		else
		if ( b.last_message )
			return vmraid.datetime.compare(a.creation, b.last_message.creation)
		else
			return vmraid.datetime.compare(a.creation, b.creation)
	}
	rooms.sort(compare)

	return rooms
}

// vmraid.chat.room.on
vmraid.provide('vmraid.chat.room.on')

/**
 * @description Triggers on Chat Room updated.
 *
 * @param {function} fn - callback with the Chat Room and Update.
 */
vmraid.chat.room.on.update = function (fn) {
	vmraid.realtime.on("vmraid.chat.room:update", r => {
		if ( r.data.last_message )
			// creation to vmraid.datetime.datetime (easier to manipulate).
			r.data = { ...r.data, last_message: { ...r.data.last_message, creation: new vmraid.datetime.datetime(r.data.last_message.creation) } }

		fn(r.room, r.data)
	})
}

/**
 * @description Triggers on Chat Room created.
 *
 * @param {function} fn - callback with the created Chat Room.
 */
vmraid.chat.room.on.create = function (fn) {
	vmraid.realtime.on("vmraid.chat.room:create", r =>
		fn({ ...r, creation: new vmraid.datetime.datetime(r.creation) })
	)
}

/**
 * @description Triggers when a User is typing in a Chat Room.
 *
 * @param {function} fn - callback with the typing User within the Chat Room.
 */
vmraid.chat.room.on.typing = function (fn) {
	vmraid.realtime.on("vmraid.chat.room:typing", r => fn(r.room, r.user))
}

// vmraid.chat.message
vmraid.provide('vmraid.chat.message')

vmraid.chat.message.typing = function (room, user) {
	vmraid.realtime.publish("vmraid.chat.message:typing", { user: user || vmraid.session.user, room: room })
}

vmraid.chat.message.send   = function (room, message, type = "Content") {
	vmraid.call("vmraid.chat.doctype.chat_message.chat_message.send",
		{ user: vmraid.session.user, room: room, content: message, type: type })
}

vmraid.chat.message.update = function (message, update, fn) {
	return new Promise(resolve => {
		vmraid.call('vmraid.chat.doctype.chat_message.chat_message.update',
			{ user: vmraid.session.user, message: message, update: update },
			r =>  {
				if ( fn )
					fn(response.message)

				resolve(response.message)
			})
	})
}

vmraid.chat.message.sort   = (messages) => {
	if ( !vmraid._.is_empty(messages) )
		messages.sort((a, b) => vmraid.datetime.compare(b.creation, a.creation))

	return messages
}

/**
 * @description Add user to seen (defaults to session.user)
 */
vmraid.chat.message.seen   = (mess, user) => {
	vmraid.call('vmraid.chat.doctype.chat_message.chat_message.seen',
		{ message: mess, user: user || vmraid.session.user })
}

vmraid.provide('vmraid.chat.message.on')
vmraid.chat.message.on.create = function (fn) {
	vmraid.realtime.on("vmraid.chat.message:create", r =>
		fn({ ...r, creation: new vmraid.datetime.datetime(r.creation) })
	)
}

vmraid.chat.message.on.update = function (fn) {
	vmraid.realtime.on("vmraid.chat.message:update", r => fn(r.message, r.data))
}

vmraid.chat.pretty_datetime   = function (date) {
	const today    = moment()
	const instance = date.moment

	if ( today.isSame(instance, "d") )
		return instance.format("hh:mm A")
	else
	if ( today.isSame(instance, "week") )
		return instance.format("dddd")
	else
		return instance.format("DD/MM/YYYY")
}

// vmraid.chat.sound
vmraid.provide('vmraid.chat.sound')

/**
 * @description Plays a given registered sound.
 *
 * @param {value} - The name of the registered sound.
 *
 * @example
 * vmraid.chat.sound.play("message")
 */
vmraid.chat.sound.play  = function (name, volume = 0.1) {
	// vmraid._.play_sound(`chat-${name}`)
	const $audio = $(`<audio class="chat-audio"/>`)
	$audio.attr('volume', volume)

	if  ( vmraid._.is_empty($audio) )
		$(document).append($audio)

	if  ( !$audio.paused ) {
		vmraid.log.info('Stopping sound playing.')
		$audio[0].pause()
		$audio.attr('currentTime', 0)
	}

	vmraid.log.info('Playing sound.')
	$audio.attr('src', `${vmraid.chat.sound.PATH}/chat-${name}.mp3`)
	$audio[0].play()
}
vmraid.chat.sound.PATH  = '/assets/vmraid/sounds'

// vmraid.chat.emoji
vmraid.chat.emojis = [ ]
vmraid.chat.emoji  = function (fn) {
	return new Promise(resolve => {
		if ( !vmraid._.is_empty(vmraid.chat.emojis) ) {
			if ( fn )
				fn(vmraid.chat.emojis)

			resolve(vmraid.chat.emojis)
		}
		else
			$.get('https://cdn.rawgit.com/vmraid/emoji/master/emoji', (data) => {
				vmraid.chat.emojis = JSON.parse(data)

				if ( fn )
					fn(vmraid.chat.emojis)

				resolve(vmraid.chat.emojis)
			})
	})
}

// Website Settings
vmraid.provide('vmraid.chat.website.settings')
vmraid.chat.website.settings = (fields, fn) =>
{
	if ( typeof fields === "function" ) {
		fn     = fields
		fields = null
	} else
	if ( typeof fields === "string" )
		fields = vmraid._.as_array(fields)

	return new Promise(resolve => {
		vmraid.call("vmraid.chat.website.settings",
			{ fields: fields })
			.then(response => {
				var message = response.message

				if ( message.enable_from )
					message   = { ...message, enable_from: new vmraid.datetime.datetime(message.enable_from, 'HH:mm:ss') }
				if ( message.enable_to )
					message   = { ...message, enable_to:   new vmraid.datetime.datetime(message.enable_to,   'HH:mm:ss') }

				if ( fn )
					fn(message)

				resolve(message)
			})
	})
}

vmraid.chat.website.token    = (fn) =>
{
	return new Promise(resolve => {
		vmraid.call("vmraid.chat.website.token")
			.then(response => {
				if ( fn )
					fn(response.message)

				resolve(response.message)
			})
	})
}

const { h, Component } = hyper

// vmraid.components
// vmraid's component namespace.
vmraid.provide('vmraid.components')

vmraid.provide('vmraid.chat.component')

/**
 * @description Button Component
 *
 * @prop {string}  type  - (Optional) "default", "primary", "info", "success", "warning", "danger" (defaults to "default")
 * @prop {boolean} block - (Optional) Render a button block (defaults to false).
 */
vmraid.components.Button
=
class extends Component {
	render ( ) {
		const { props } = this
		const size      = vmraid.components.Button.SIZE[props.size]

		return (
			h("button", { ...props, class: `btn ${size && size.class} btn-${props.type} ${props.block ? "btn-block" : ""} ${props.class ? props.class : ""}` },
				props.children
			)
		)
	}
}
vmraid.components.Button.SIZE
=
{
	small: {
		class: "btn-sm"
	},
	large: {
		class: "btn-lg"
	}
}
vmraid.components.Button.defaultProps
=
{
	 type: "default",
	block: false
}

/**
 * @description FAB Component
 *
 * @extends vmraid.components.Button
 */
vmraid.components.FAB
=
class extends vmraid.components.Button {
	render ( ) {
		const { props } = this
		const size      = vmraid.components.FAB.SIZE[props.size]

		return (
			h(vmraid.components.Button, { ...props, class: `${props.class} ${size && size.class}`},
				h("i", { class: props.icon })
			)
		)
	}
}
vmraid.components.FAB.defaultProps
=
{
	icon: "octicon octicon-plus"
}
vmraid.components.FAB.SIZE
=
{
	small:
	{
		class: "vmraid-fab-sm"
	},
	large:
	{
		class: "vmraid-fab-lg"
	}
}

/**
 * @description Octicon Component
 *
 * @prop color - (Required) color for the indicator
 */
vmraid.components.Indicator
=
class extends Component {
	render ( ) {
		const { props } = this

		return props.color ? h("span", { ...props, class: `indicator ${props.color}` }) : null
	}
}

/**
 * @description FontAwesome Component
 */
vmraid.components.FontAwesome
=
class extends Component {
	render ( ) {
		const { props } = this

		return props.type ? h("i", { ...props, class: `fa ${props.fixed ? "fa-fw" : ""} fa-${props.type} ${props.class}` }) : null
	}
}
vmraid.components.FontAwesome.defaultProps
=
{
	fixed: false
}

/**
 * @description Octicon Component
 *
 * @extends vmraid.Component
 */
vmraid.components.Octicon
=
class extends Component {
	render ( ) {
		const { props } = this

		return props.type ? h("i", { ...props, class: `octicon octicon-${props.type}` }) : null
	}
}

/**
 * @description Avatar Component
 *
 * @prop {string} title - (Optional) title for the avatar.
 * @prop {string} abbr  - (Optional) abbreviation for the avatar, defaults to the first letter of the title.
 * @prop {string} size  - (Optional) size of the avatar to be displayed.
 * @prop {image}  image - (Optional) image for the avatar, defaults to the first letter of the title.
 */
vmraid.components.Avatar
=
class extends Component {
	render ( ) {
		const { props } = this
		const abbr      = props.abbr || props.title.substr(0, 1)
		const size      = vmraid.components.Avatar.SIZE[props.size] || vmraid.components.Avatar.SIZE.medium

		return (
			h("span", { class: `avatar ${size.class} ${props.class ? props.class : ""}` },
				props.image ?
					h("img", { class: "media-object", src: props.image })
					:
					h("div", { class: "standard-image" }, abbr)
			)
		)
	}
}
vmraid.components.Avatar.SIZE
=
{
	small:
	{
		class: "avatar-small"
	},
	large:
	{
		class: "avatar-large"
	},
	medium:
	{
		class: "avatar-medium"
	}
}

/**
 * @description VMRaid Chat Object.
 *
 * @example
 * const chat = new vmraid.Chat(options) // appends to "body"
 * chat.render()
 * const chat = new vmraid.Chat(".selector", options)
 * chat.render()
 *
 * const chat = new vmraid.Chat()
 * chat.set_wrapper('.selector')
 *     .set_options(options)
 *     .render()
 */
vmraid.Chat
=
class {
	/**
	 * @description VMRaid Chat Object.
	 *
	 * @param {string} selector - A query selector, HTML Element or jQuery object.
	 * @param {object} options  - Optional configurations.
	 */
	constructor (selector, options) {
		if ( !(typeof selector === "string" || selector instanceof $ || selector instanceof HTMLElement) ) {
			options  = selector
			selector = null
		}

		this.options = vmraid.Chat.OPTIONS

		this.set_wrapper(selector ? selector : "body")
		this.set_options(options)

	}

	/**
	 * Set the container on which the chat widget is mounted on.
	 * @param   {string|HTMLElement} selector - A query selector, HTML Element or jQuery object.
	 *
	 * @returns {vmraid.Chat}                 - The instance.
	 *
	 * @example
	 * const chat = new vmraid.Chat()
	 * chat.set_wrapper(".selector")
	 */
	set_wrapper (selector) {
		this.$wrapper = $(selector)

		return this
	}

	/**
	 * Set the configurations for the chat interface.
	 * @param   {object}      options - Optional Configurations.
	 *
	 * @returns {vmraid.Chat}         - The instance.
	 *
	 * @example
	 * const chat = new vmraid.Chat()
	 * chat.set_options({ layout: vmraid.Chat.Layout.PAGE })
	 */
	set_options (options) {
		this.options = { ...this.options, ...options }

		return this
	}

	/**
	 * @description Destory the chat widget.
	 *
	 * @returns {vmraid.Chat} - The instance.
	 *
	 * @example
	 * const chat = new vmraid.Chat()
	 * chat.render()
	 *     .destroy()
	 */
	destroy ( ) {
		const $wrapper = this.$wrapper
		$wrapper.remove(".vmraid-chat")

		return this
	}

	/**
	 * @description Render the chat widget component onto destined wrapper.
	 *
	 * @returns {vmraid.Chat} - The instance.
	 *
	 * @example
	 * const chat = new vmraid.Chat()
	 * chat.render()
	 */
	render (props = { }) {
		this.destroy()

		const $wrapper   = this.$wrapper
		const options    = this.options

		const component  = h(vmraid.Chat.Widget, {
			layout: options.layout,
			target: options.target,
			...props
		})

		hyper.render(component, $wrapper[0])

		return this
	}
}
vmraid.Chat.Layout
=
{
	PAGE: "page", POPPER: "popper"
}
vmraid.Chat.OPTIONS
=
{
	layout: vmraid.Chat.Layout.POPPER
}

/**
 * @description The base Component for VMRaid Chat
 */
vmraid.Chat.Widget
=
class extends Component {
	constructor (props) {
		super (props)

		this.setup(props)
		this.make()
	}

	setup (props) {
		// room actions
		this.room           = { }
		this.room.add       = rooms => {
			rooms           = vmraid._.as_array(rooms)
			const names     = rooms.map(r => r.name)

			vmraid.log.info(`Subscribing ${vmraid.session.user} to Chat Rooms ${names.join(", ")}.`)
			vmraid.chat.room.subscribe(names)

			const state     = [ ]

			for (const room of rooms)
				  if ( ["Group", "Visitor"].includes(room.type) || room.owner === vmraid.session.user || room.last_message || room.users.includes(vmraid.session.user)) {
					vmraid.log.info(`Adding ${room.name} to component.`)
					state.push(room)
				}

			this.set_state({ rooms: [ ...this.state.rooms, ...state ] })
		}
		this.room.update    = (room, update) => {
			const { state } = this
			var   exists    = false
			const rooms     = state.rooms.map(r => {
				if ( r.name === room ) {
					exists  = true
					if ( update.typing ) {
						if ( !vmraid._.is_empty(r.typing) ) {
							const usr = update.typing
							if ( !r.typing.includes(usr) ) {
								update.typing = vmraid._.copy_array(r.typing)
								update.typing.push(usr)
							}
						}
						else
							update.typing = vmraid._.as_array(update.typing)
					}

					return { ...r, ...update }
				}

				return r
			})

			if ( vmraid.session.user !== 'Guest' ) {
				if ( !exists )
					vmraid.chat.room.get(room, (room) => this.room.add(room))
				else
					this.set_state({ rooms })
			}

			if ( state.room.name === room ) {
				if ( update.typing ) {
					if ( !vmraid._.is_empty(state.room.typing) ) {
						const usr = update.typing
						if ( !state.room.typing.includes(usr) ) {
							update.typing = vmraid._.copy_array(state.room.typing)
							update.typing.push(usr)
						}
					} else
						update.typing = vmraid._.as_array(update.typing)
				}

				const room  = { ...state.room, ...update }

				this.set_state({ room })
			}
		}
		this.room.select    = (name) => {
			vmraid.chat.room.history(name, (messages) => {
				const  { state } = this
				const room       = state.rooms.find(r => r.name === name)

				this.set_state({
					room: { ...state.room, ...room, messages: messages }
				})
			})
		}

		this.state = { ...vmraid.Chat.Widget.defaultState, ...props }
	}

	make ( ) {
		if ( vmraid.session.user !== 'Guest' ) {
			vmraid.chat.profile.create([
				"status", "message_preview", "notification_tones", "conversation_tones"
			]).then(profile => {
				this.set_state({ profile })

				vmraid.chat.room.get(rooms => {
					rooms = vmraid._.as_array(rooms)
					vmraid.log.info(`User ${vmraid.session.user} is subscribed to ${rooms.length} ${vmraid._.pluralize('room', rooms.length)}.`)

					if ( !vmraid._.is_empty(rooms) )
						this.room.add(rooms)
				})

				this.bind()
			})
		} else {
			this.bind()
		}
	}

	bind ( ) {
		vmraid.chat.profile.on.update((user, update) => {
			vmraid.log.warn(`TRIGGER: Chat Profile update ${JSON.stringify(update)} of User ${user}.`)

			if ( 'status' in update ) {
				if ( user === vmraid.session.user ) {
					this.set_state({
						profile: { ...this.state.profile, status: update.status }
					})
				} else {
					const status = vmraid.chat.profile.STATUSES.find(s => s.name === update.status)
					const color  = status.color

					const alert  = `<span class="indicator ${color}"/> ${vmraid.user.full_name(user)} is currently <b>${update.status}</b>`
					vmraid.show_alert(alert, 3)
				}
			}
		})

		vmraid.chat.room.on.create((room) => {
			vmraid.log.warn(`TRIGGER: Chat Room ${room.name} created.`)
			this.room.add(room)
		})

		vmraid.chat.room.on.update((room, update) => {
			vmraid.log.warn(`TRIGGER: Chat Room ${room} update ${JSON.stringify(update)} recieved.`)
			this.room.update(room, update)
		})

		vmraid.chat.room.on.typing((room, user) => {
			if ( user !== vmraid.session.user ) {
				vmraid.log.warn(`User ${user} typing in Chat Room ${room}.`)
				this.room.update(room, { typing: user })

				setTimeout(() => this.room.update(room, { typing: null }), 5000)
			}
		})

		vmraid.chat.message.on.create((r) => {
			const { state } = this

			// play sound.
			if ( state.room.name )
				state.profile.conversation_tones && vmraid.chat.sound.play('message')
			else
				state.profile.notification_tones && vmraid.chat.sound.play('notification')

			if ( r.user !== vmraid.session.user && state.profile.message_preview && !state.toggle ) {
				const $element = $('body').find('.vmraid-chat-alert')
				$element.remove()

				const  alert   = // TODO: ellipses content
				`
				<span data-action="show-message" class="cursor-pointer">
					<span class="indicator yellow"/>
						<span class="avatar avatar-small">
							<span class="avatar-frame" style="background-image: url(${vmraid.user.image(r.user)})"></span>
						</span>
						<b>${vmraid.user.first_name(r.user)}</b>: ${r.content}
				</span>
				`
				vmraid.show_alert(alert, 15, {
					"show-message": function (r) {
						this.room.select(r.room)
						this.base.firstChild._component.toggle()
					}.bind(this, r)
				})
				vmraid.notify(`${vmraid.user.first_name(r.user)}`, {
					body: r.content,
					icon: vmraid.user.image(r.user),
					tag: r.user
				})
			}

			if ( r.room === state.room.name ) {
				const mess  = vmraid._.copy_array(state.room.messages)
				mess.push(r)

				this.set_state({ room: { ...state.room, messages: mess } })
			}
		})

		vmraid.chat.message.on.update((message, update) => {
			vmraid.log.warn(`TRIGGER: Chat Message ${message} update ${JSON.stringify(update)} recieved.`)
		})
	}

	render ( ) {
		const { props, state } = this
		const me               = this

		const ActionBar        = h(vmraid.Chat.Widget.ActionBar, {
			placeholder: __("Search or Create a New Chat"),
				  class: "level",
				 layout: props.layout,
				actions:
			vmraid._.compact([
				{
					  label: __("New"),
					onclick: function ( ) {
						const dialog = new vmraid.ui.Dialog({
							  title: __("New Chat"),
							 fields: [
								 {
										 label: __("Chat Type"),
									 fieldname: "type",
									 fieldtype: "Select",
									   options: ["Group", "Direct Chat"],
									   default: "Group",
									  onchange: () =>  {
											const type     = dialog.get_value("type")
											const is_group = type === "Group"

											dialog.set_df_property("group_name", "reqd",  is_group)
											dialog.set_df_property("user",       "reqd", !is_group)
									  }
								 },
								 {
										 label: __("Group Name"),
									 fieldname: "group_name",
									 fieldtype: "Data",
										  reqd: true,
									depends_on: "eval:doc.type == 'Group'"
								 },
								 {
										 label: __("Users"),
									 fieldname: "users",
									 fieldtype: "MultiSelect",
									   options: vmraid.user.get_emails(),
									depends_on: "eval:doc.type == 'Group'"
								 },
								 {
										 label: __("User"),
									 fieldname: "user",
									 fieldtype: "Link",
									   options: "User",
									depends_on: "eval:doc.type == 'Direct Chat'"
								 }
							 ],
							action: {
								primary: {
									   label: __('Create'),
									onsubmit: (values) => {
										if ( values.type === "Group" ) {
											if ( !vmraid._.is_empty(values.users) ) {
												const name  = values.group_name
												const users = dialog.fields_dict.users.get_values()

												vmraid.chat.room.create("Group",  null, users, name)
											}
										} else {
											const user      = values.user

											vmraid.chat.room.create("Direct", null, user)
										}
										dialog.hide()
									}
								}
							}
						})
						dialog.show()
					}
				},
				vmraid._.is_mobile() && {
					   icon: "octicon octicon-x",
					   class: "vmraid-chat-close",
					onclick: () => this.set_state({ toggle: false })
				}
			], Boolean),
			change: query => { me.set_state({ query }) },
			  span: span  => { me.set_state({ span  }) },
		})

		var   contacts   = [ ]
		if ( 'user_info' in vmraid.boot ) {
			const emails = vmraid.user.get_emails()
			for (const email of emails) {
				var exists = false

				for (const room of state.rooms) {
					if ( room.type === 'Direct' ) {
						if ( room.owner === email || vmraid._.squash(room.users) === email )
							exists = true
					}
				}

				if ( !exists )
					contacts.push({ owner: vmraid.session.user, users: [email] })
			}
		}
		const rooms      = state.query ? vmraid.chat.room.search(state.query, state.rooms.concat(contacts)) : vmraid.chat.room.sort(state.rooms)

		const layout     = state.span  ? vmraid.Chat.Layout.PAGE : vmraid.Chat.Layout.POPPER

		const RoomList   = vmraid._.is_empty(rooms) && !state.query ?
			h("div", { class: "vcenter" },
				h("div", { class: "text-center text-extra-muted" },
					h("p","",__("You don't have any messages yet."))
				)
			)
			:
			h(vmraid.Chat.Widget.RoomList, { rooms: rooms, click: room =>  {
				if ( room.name )
					this.room.select(room.name)
				else
					vmraid.chat.room.create("Direct", room.owner, vmraid._.squash(room.users), ({ name }) => this.room.select(name))
			}})
		const Room       = h(vmraid.Chat.Widget.Room, { ...state.room, layout: layout, destroy: () => {
			this.set_state({
				room: { name: null, messages: [ ] }
			})
		}})

		const component  = layout === vmraid.Chat.Layout.POPPER ?
			h(vmraid.Chat.Widget.Popper, { heading: ActionBar, page: state.room.name && Room, target: props.target,
				toggle: (t) => this.set_state({ toggle: t }) },
				RoomList
			)
			:
			h("div", { class: "vmraid-chat-popper" },
				h("div", { class: "vmraid-chat-popper-collapse" },
					h("div", { class: "panel panel-default panel-span", style: { width: "25%" } },
						h("div", { class: "panel-heading" },
							ActionBar
						),
						RoomList
					),
					Room
				)
			)

		return (
			h("div", { class: "vmraid-chat" },
				component
			)
		)
	}
}
vmraid.Chat.Widget.defaultState =  {
	  query: "",
	profile: { },
	  rooms: [ ],
	   room: { name: null, messages: [ ], typing: [ ] },
	 toggle: false,
	   span: false
}
vmraid.Chat.Widget.defaultProps = {
	layout: vmraid.Chat.Layout.POPPER
}

/**
 * @description Chat Widget Popper HOC.
 */
vmraid.Chat.Widget.Popper
=
class extends Component {
	constructor (props) {
		super (props)

		this.setup(props);
	}

	setup (props) {
		this.toggle = this.toggle.bind(this)

		this.state  = vmraid.Chat.Widget.Popper.defaultState

		if ( props.target )
			$(props.target).click(() => this.toggle())

		vmraid.chat.widget = this
	}

	toggle  (active) {
		let toggle
		if ( arguments.length === 1 )
			toggle = active
		else
			toggle = this.state.active ? false : true

		this.set_state({ active: toggle })

		this.props.toggle(toggle)
	}

	on_mounted ( ) {
		$(document.body).on('click', '.page-container, .vmraid-chat-close', ({ currentTarget }) => {
			this.toggle(false)
		})
	}

	render  ( )  {
		const { props, state } = this

		return !state.destroy ?
		(
			h("div", { class: "vmraid-chat-popper", style: !props.target ? { "margin-bottom": "80px" } : null },
				!props.target ?
					h(vmraid.components.FAB, {
						  class: "vmraid-fab",
						   icon: state.active ? "fa fa-fw fa-times" : "font-heavy octicon octicon-comment",
						   size: vmraid._.is_mobile() ? null : "large",
						   type: "primary",
						onclick: () => this.toggle(),
					}) : null,
				state.active ?
					h("div", { class: "vmraid-chat-popper-collapse" },
						props.page ? props.page : (
							h("div", { class: `panel panel-default ${vmraid._.is_mobile() ? "panel-span" : ""}` },
								h("div", { class: "panel-heading" },
									props.heading
								),
								props.children
							)
						)
				) : null
			)
		) : null
	}
}
vmraid.Chat.Widget.Popper.defaultState
=
{
	 active: false,
	destroy: false
}

/**
 * @description vmraid.Chat.Widget ActionBar Component
 */
vmraid.Chat.Widget.ActionBar
=
class extends Component {
	constructor (props) {
		super (props)

		this.change = this.change.bind(this)
		this.submit = this.submit.bind(this)

		this.state  = vmraid.Chat.Widget.ActionBar.defaultState
	}

	change (e) {
		const { props, state } = this

		this.set_state({
			[e.target.name]: e.target.value
		})

		props.change(state.query)
	}

	submit (e) {
		const { props, state } = this

		e.preventDefault()

		props.submit(state.query)
	}

	render ( ) {
		const me               = this
		const { props, state } = this
		const { actions }      = props

		return (
			h("div", { class: `vmraid-chat-action-bar ${props.class ? props.class : ""}` },
				h("form", { oninput: this.change, onsubmit: this.submit },
					h("input", { autocomplete: "off", class: "form-control input-sm", name: "query", value: state.query, placeholder: props.placeholder || "Search" }),
				),
				!vmraid._.is_empty(actions) ?
					actions.map(action => h(vmraid.Chat.Widget.ActionBar.Action, { ...action })) : null,
				!vmraid._.is_mobile() ?
					h(vmraid.Chat.Widget.ActionBar.Action, {
						icon: `octicon octicon-screen-${state.span ? "normal" : "full"}`,
						onclick: () => {
							const span = !state.span
							me.set_state({ span })
							props.span(span)
						}
					})
					:
					null
			)
		)
	}
}
vmraid.Chat.Widget.ActionBar.defaultState
=
{
	query: null,
	 span: false
}

/**
 * @description vmraid.Chat.Widget ActionBar's Action Component.
 */
vmraid.Chat.Widget.ActionBar.Action
=
class extends Component {
	render ( ) {
		const { props } = this

		return (
			h(vmraid.components.Button, { size: "small", class: "btn-action", ...props },
				props.icon ? h("i", { class: props.icon }) : null,
				`${props.icon ? " " : ""}${props.label ? props.label : ""}`
			)
		)
	}
}

/**
 * @description vmraid.Chat.Widget RoomList Component
 */
vmraid.Chat.Widget.RoomList
=
class extends Component {
	render ( ) {
		const { props } = this
		const rooms     = props.rooms

		return !vmraid._.is_empty(rooms) ? (
			h("ul", { class: "vmraid-chat-room-list nav nav-pills nav-stacked" },
				rooms.map(room => h(vmraid.Chat.Widget.RoomList.Item, { ...room, click: props.click }))
			)
		) : null
	}
}

/**
 * @description vmraid.Chat.Widget RoomList's Item Component
 */
vmraid.Chat.Widget.RoomList.Item
=
class extends Component {
	render ( ) {
		const { props }    = this
		const item         = { }

		if ( props.type === "Group" ) {
			item.title     = props.room_name
			item.image     = props.avatar

			if ( !vmraid._.is_empty(props.typing) ) {
				props.typing  = vmraid._.as_array(props.typing) // HACK: (BUG) why does typing return a string?
				const names   = props.typing.map(user => vmraid.user.first_name(user))
				item.subtitle = `${names.join(", ")} typing...`
			} else
			if ( props.last_message ) {
				const message = props.last_message
				const content = message.content

				if ( message.type === "File" ) {
					item.subtitle = `📁 ${content.name}`
				} else {
					item.subtitle = props.last_message.content
				}
			}
		} else {
			const user     = props.owner === vmraid.session.user ? vmraid._.squash(props.users) : props.owner

			item.title     = vmraid.user.full_name(user)
			item.image     = vmraid.user.image(user)
			item.abbr      = vmraid.user.abbr(user)

			if ( !vmraid._.is_empty(props.typing) )
				item.subtitle = 'typing...'
			else
			if ( props.last_message ) {
				const message = props.last_message
				const content = message.content

				if ( message.type === "File" ) {
					item.subtitle = `📁 ${content.name}`
				} else {
					item.subtitle = props.last_message.content
				}
			}
		}

		let is_unread = false
		if ( props.last_message ) {
			item.timestamp = vmraid.chat.pretty_datetime(props.last_message.creation)
			is_unread = !props.last_message.seen.includes(vmraid.session.user)
		}

		return (
			h("li", null,
				h("a", { class: props.active ? "active": "", onclick: () => {
					if (props.last_message) {
						vmraid.chat.message.seen(props.last_message.name);
					}
					props.click(props)
				} },
					h("div", { class: "row" },
						h("div", { class: "col-xs-9" },
							h(vmraid.Chat.Widget.MediaProfile, { ...item })
						),
						h("div", { class: "col-xs-3 text-right" },
							[
								h("div", { class: "text-muted", style: { "font-size": "9px" } }, item.timestamp),
								is_unread ? h("span", { class: "indicator red" }) : null
							]
						),
					)
				)
			)
		)
	}
}

/**
 * @description vmraid.Chat.Widget's MediProfile Component.
 */
vmraid.Chat.Widget.MediaProfile
=
class extends Component {
	render ( ) {
		const { props } = this
		const position  = vmraid.Chat.Widget.MediaProfile.POSITION[props.position || "left"]
		const avatar    = (
			h("div", { class: `${position.class} media-middle` },
				h(vmraid.components.Avatar, { ...props,
					title: props.title,
					image: props.image,
					 size: props.size,
					 abbr: props.abbr
				})
			)
		)

		return (
			h("div", { class: "media", style: position.class === "media-right" ? { "text-align": "right" } : null },
				position.class === "media-left"  ? avatar : null,
				h("div", { class: "media-body" },
					h("div", { class: "media-heading ellipsis small", style: `max-width: ${props.width_title || "100%"} display: inline-block` }, props.title),
					props.content  ? h("div","",h("small","",props.content))  : null,
					props.subtitle ? h("div",{ class: "media-subtitle small" },h("small", { class: "text-muted" }, props.subtitle)) : null
				),
				position.class === "media-right" ? avatar : null
			)
		)
	}
}
vmraid.Chat.Widget.MediaProfile.POSITION
=
{
	left: { class: "media-left" }, right: { class: "media-right" }
}

/**
 * @description vmraid.Chat.Widget Room Component
 */
vmraid.Chat.Widget.Room
=
class extends Component {
	render ( ) {
		const { props, state } = this
		const hints            =
		[
			{
				 match: /@(\w*)$/,
				search: function (keyword, callback) {
					if ( props.type === 'Group' ) {
						const query = keyword.slice(1)
						const users = [].concat(vmraid._.as_array(props.owner), props.users)
						const grep  = users.filter(user => user !== vmraid.session.user && user.indexOf(query) === 0)

						callback(grep)
					}
				},
				component: function (item) {
					return (
						h(vmraid.Chat.Widget.MediaProfile, {
							title: vmraid.user.full_name(item),
							image: vmraid.user.image(item),
							 size: "small"
						})
					)
				}
			},
			{
				match: /:([a-z]*)$/,
			   search: function (keyword, callback) {
					vmraid.chat.emoji(function (emojis) {
						const query = keyword.slice(1)
						const items = [ ]
						for (const emoji of emojis)
							for (const alias of emoji.aliases)
								if ( alias.indexOf(query) === 0 )
									items.push({ name: alias, value: emoji.emoji })

						callback(items)
					})
			   },
				 content: (item) => item.value,
			   component: function (item) {
					return (
						h(vmraid.Chat.Widget.MediaProfile, {
							title: item.name,
							 abbr: item.value,
							 size: "small"
						})
					)
			   }
		   }
		]

		const actions = vmraid._.compact([
			!vmraid._.is_mobile() && {
				 icon: "camera",
				label: "Camera",
				onclick: ( ) => {
					const capture = new vmraid.ui.Capture({
						animate: false,
						  error: true
					})
					capture.show()

					capture.submit(data_url => {
						// data_url
					})
				}
			},
			{
				 icon: "file",
				label: "File",
				onclick: ( ) => {
					new vmraid.ui.FileUploader({
						doctype: "Chat Room",
						docname: props.name,
						on_success(file_doc) {
							const { file_url, filename } = file_doc
							vmraid.chat.message.send(props.name, { path: file_url, name: filename }, "File")
						}
					})
				}
			}
		])

		if ( vmraid.session.user !== 'Guest' ) {
			if (props.messages) {
				props.messages = vmraid._.as_array(props.messages)
				for (const message of props.messages)
					if ( !message.seen.includes(vmraid.session.user) )
						vmraid.chat.message.seen(message.name)
					else
						break
			}
		}

		return (
			h("div", { class: `panel panel-default
				${props.name ? "panel-bg" : ""}
				${props.layout === vmraid.Chat.Layout.PAGE || vmraid._.is_mobile() ? "panel-span" : ""}`,
				style: props.layout === vmraid.Chat.Layout.PAGE && { width: "75%", left: "25%", "box-shadow": "none" } },
				props.name && h(vmraid.Chat.Widget.Room.Header, { ...props, on_back: props.destroy }),
				props.name ?
					!vmraid._.is_empty(props.messages) ?
						h(vmraid.chat.component.ChatList, {
							messages: props.messages
						})
						:
						h("div", { class: "panel-body", style: { "height": "100%" } },
							h("div", { class: "vcenter" },
								h("div", { class: "text-center text-extra-muted" },
									h(vmraid.components.Octicon, { type: "comment-discussion", style: "font-size: 48px" }),
									h("p","",__("Start a conversation."))
								)
							)
						)
					:
					h("div", { class: "panel-body", style: { "height": "100%" } },
						h("div", { class: "vcenter" },
							h("div", { class: "text-center text-extra-muted" },
								h(vmraid.components.Octicon, { type: "comment-discussion", style: "font-size: 125px" }),
								h("p","",__("Select a chat to start messaging."))
							)
						)
					),
				props.name ?
					h("div", { class: "chat-room-footer" },
						h(vmraid.chat.component.ChatForm, { actions: actions,
							onchange: () => {
								vmraid.chat.message.typing(props.name)
							},
							onsubmit: (message) => {
								vmraid.chat.message.send(props.name, message)
							},
							hint: hints
						})
					)
					:
					null
			)
		)
	}
}

vmraid.Chat.Widget.Room.Header
=
class extends Component {
	render ( ) {
		const { props }     = this

		const item          = { }

		if ( ["Group", "Visitor"].includes(props.type) ) {
			item.route      = `chat-room/${props.name}`

			item.title      = props.room_name
			item.image      = props.avatar

			if ( !vmraid._.is_empty(props.typing) ) {
				props.typing  = vmraid._.as_array(props.typing) // HACK: (BUG) why does typing return as a string?
				const users   = props.typing.map(user => vmraid.user.first_name(user))
				item.subtitle = `${users.join(", ")} typing...`
			} else
				item.subtitle = props.type === "Group" ?
					`${props.users.length} ${vmraid._.pluralize('member', props.users.length)}`
					: ""
		}
		else {
			const user      = props.owner === vmraid.session.user ? vmraid._.squash(props.users) : props.owner

			item.route      = `user/${user}`

			item.title      = vmraid.user.full_name(user)
			item.image      = vmraid.user.image(user)

			if ( !vmraid._.is_empty(props.typing) )
				item.subtitle = 'typing...'
		}

		const popper        = props.layout === vmraid.Chat.Layout.POPPER || vmraid._.is_mobile()

		return (
			h("div", { class: "panel-heading", style: { "height": "50px" } }, // sorry. :(
				h("div", { class: "level" },
					popper && vmraid.session.user !== "Guest" ?
						h(vmraid.components.Button,{class:"btn-back",onclick:props.on_back},
							h(vmraid.components.Octicon, { type: "chevron-left" })
						) : null,
					h("div","",
						h("div", { class: "panel-title" },
							h("div", { class: "cursor-pointer", onclick: () => {
								vmraid.session.user !== "Guest" ?
									vmraid.set_route(item.route) : null;
							}},
								h(vmraid.Chat.Widget.MediaProfile, { ...item })
							)
						)
					),
					h("div", { class: popper ? "col-xs-2"  : "col-xs-3" },
						h("div", { class: "text-right" },
							vmraid._.is_mobile() && h(vmraid.components.Button, { class: "vmraid-chat-close", onclick: props.toggle },
								h(vmraid.components.Octicon, { type: "x" })
							)
						)
					)
				)
			)
		)
	}
}

/**
 * @description ChatList Component
 *
 * @prop {array} messages - ChatMessage(s)
 */
vmraid.chat.component.ChatList
=
class extends Component {
	on_mounted ( ) {
		this.$element  = $('.vmraid-chat').find('.chat-list')
		this.$element.scrollTop(this.$element[0].scrollHeight)
	}

	on_updated ( ) {
		this.$element.scrollTop(this.$element[0].scrollHeight)
	}

	render ( ) {
		var messages = [ ]
		for (var i   = 0 ; i < this.props.messages.length ; ++i) {
			var   message   = this.props.messages[i]
			const me        = message.user === vmraid.session.user

			if ( i === 0 || !vmraid.datetime.equal(message.creation, this.props.messages[i - 1].creation, 'day') )
				messages.push({ type: "Notification", content: message.creation.format('MMMM DD') })

			messages.push(message)
		}

		return (
			h("div",{class:"chat-list list-group"},
				!vmraid._.is_empty(messages) ?
					messages.map(m => h(vmraid.chat.component.ChatList.Item, {...m})) : null
			)
		)
	}
}

/**
 * @description ChatList.Item Component
 *
 * @prop {string} name       - ChatMessage name
 * @prop {string} user       - ChatMessage user
 * @prop {string} room       - ChatMessage room
 * @prop {string} room_type  - ChatMessage room_type ("Direct", "Group" or "Visitor")
 * @prop {string} content    - ChatMessage content
 * @prop {vmraid.datetime.datetime} creation - ChatMessage creation
 *
 * @prop {boolean} groupable - Whether the ChatMessage is groupable.
 */
vmraid.chat.component.ChatList.Item
=
class extends Component {
	render ( ) {
		const { props } = this

		const me        = props.user === vmraid.session.user
		const content   = props.content

		return (
			h("div",{class: "chat-list-item list-group-item"},
				props.type === "Notification" ?
					h("div",{class:"chat-list-notification"},
						h("div",{class:"chat-list-notification-content"},
							content
						)
					)
					:
					h("div",{class:`${me ? "text-right" : ""}`},
						props.room_type === "Group" && !me ?
							h(vmraid.components.Avatar, {
								title: vmraid.user.full_name(props.user),
								image: vmraid.user.image(props.user)
							}) : null,
						h(vmraid.chat.component.ChatBubble, props)
					)
			)
		)
	}
}

/**
 * @description ChatBubble Component
 *
 * @prop {string} name       - ChatMessage name
 * @prop {string} user       - ChatMessage user
 * @prop {string} room       - ChatMessage room
 * @prop {string} room_type  - ChatMessage room_type ("Direct", "Group" or "Visitor")
 * @prop {string} content    - ChatMessage content
 * @prop {vmraid.datetime.datetime} creation - ChatMessage creation
 *
 * @prop {boolean} groupable - Whether the ChatMessage is groupable.
 */
vmraid.chat.component.ChatBubble
=
class extends Component {
	constructor (props) {
		super (props)

		this.onclick = this.onclick.bind(this)
	}

	onclick ( ) {
		const { props } = this
		if ( props.user === vmraid.session.user ) {
			vmraid.quick_edit("Chat Message", props.name, (values) => {

			})
		}
	}

	render  ( ) {
		const { props } = this
		const creation 	= props.creation.format('hh:mm A')

		const me        = props.user === vmraid.session.user
		const read      = !vmraid._.is_empty(props.seen) && !props.seen.includes(vmraid.session.user)

		const content   = props.content

		return (
			h("div",{class:`chat-bubble ${props.groupable ? "chat-groupable" : ""} chat-bubble-${me ? "r" : "l"}`,
				onclick: this.onclick},
				props.room_type === "Group" && !me ?
					h("div",{class:"chat-bubble-author"},
					h("a", { onclick: () => { vmraid.set_route('Form', 'User', props.user) } },
						vmraid.user.full_name(props.user)
					)
					) : null,
				h("div",{class:"chat-bubble-content"},
						h("small","",
							props.type === "File" ?
								h("a", { class: "no-decoration", href: content.path, target: "_blank" },
									h(vmraid.components.FontAwesome, { type: "file", fixed: true }), ` ${content.name}`
								)
								:
								content
						)
				),
				h("div",{class:"chat-bubble-meta"},
					h("span",{class:"chat-bubble-creation"},creation),
					me && read ?
						h("span",{class:"chat-bubble-check"},
							h(vmraid.components.Octicon,{type:"check"})
						) : null
				)
			)
		)
	}
}

/**
 * @description ChatForm Component
 */
vmraid.chat.component.ChatForm
=
class extends Component {
	constructor (props) {
		super (props)

		this.onchange   = this.onchange.bind(this)
		this.onsubmit   = this.onsubmit.bind(this)

		this.hint        = this.hint.bind(this)

		this.state       = vmraid.chat.component.ChatForm.defaultState
	}

	onchange (e) {
		const { props, state } = this
		const value            = e.target.value

		this.set_state({
			[e.target.name]: value
		})

		props.onchange(state)

		this.hint(value)
	}

	hint (value) {
		const { props, state } = this

		if ( props.hint ) {
			const tokens =  value.split(" ")
			const sliced = tokens.slice(0, tokens.length - 1)

			const token  = tokens[tokens.length - 1]

			if ( token ) {
				props.hint   = vmraid._.as_array(props.hint)
				const hint   = props.hint.find(hint => hint.match.test(token))

				if ( hint ) {
					hint.search(token, items => {
						const hints = items.map(item => {
							// You should stop writing one-liners! >_>
							const replace = token.replace(hint.match, hint.content ? hint.content(item) : item)
							const content = `${sliced.join(" ")} ${replace}`.trim()
							item          = { component: hint.component(item), content: content }

							return item
						}).slice(0, hint.max || 5)

						this.set_state({ hints })
					})
				}
				else
					this.set_state({ hints: [ ] })
			} else
				this.set_state({ hints: [ ] })
		}
	}

	onsubmit (e) {
		e.preventDefault()

		if ( this.state.content ) {
			this.props.onsubmit(this.state.content)

			this.set_state({ content: null })
		}
	}

	render ( ) {
		const { props, state } = this

		return (
			h("div",{class:"chat-form"},
				state.hints.length ?
					h("ul", { class: "hint-list list-group" },
						state.hints.map((item) => {
							return (
								h("li", { class: "hint-list-item list-group-item" },
									h("a", { href: "javascript:void(0)", onclick: () => {
										this.set_state({ content: item.content, hints: [ ] })
									}},
										item.component
									)
								)
							)
						})
					) : null,
				h("form", { oninput: this.onchange, onsubmit: this.onsubmit },
					h("div",{class:"input-group input-group-lg"},
						!vmraid._.is_empty(props.actions) ?
							h("div",{class:"input-group-btn dropup"},
								h(vmraid.components.Button,{ class: (vmraid.session.user === "Guest" ? "disabled" : "dropdown-toggle"), "data-toggle": "dropdown"},
									h(vmraid.components.FontAwesome, { class: "text-muted", type: "paperclip", fixed: true })
								),
								h("div",{ class:"dropdown-menu dropdown-menu-left", onclick: e => e.stopPropagation() },
									!vmraid._.is_empty(props.actions) && props.actions.map((action) => {
										return (
											h("li", null,
												h("a",{onclick:action.onclick},
													h(vmraid.components.FontAwesome,{type:action.icon,fixed:true}), ` ${action.label}`,
												)
											)
										)
									})
								)
							) : null,
						h("textarea", {
									class: "form-control",
									 name: "content",
									value: state.content,
							  placeholder: "Type a message",
								autofocus: true,
							   onkeypress: (e) => {
									if ( e.which === vmraid.ui.keycode.RETURN && !e.shiftKey )
										this.onsubmit(e)
							   }
						}),
						h("div",{class:"input-group-btn"},
							h(vmraid.components.Button, { onclick: this.onsubmit },
								h(vmraid.components.FontAwesome, { class: !vmraid._.is_empty(state.content) ? "text-primary" : "text-muted", type: "send", fixed: true })
							),
						)
					)
				)
			)
		)
	}
}
vmraid.chat.component.ChatForm.defaultState
=
{
	content: null,
	  hints: [ ],
}

/**
 * @description EmojiPicker Component
 *
 * @todo Under Development
 */
vmraid.chat.component.EmojiPicker
=
class extends Component  {
	render ( ) {
		const { props } = this

		return (
			h("div", { class: `vmraid-chat-emoji dropup ${props.class}` },
				h(vmraid.components.Button, { type: "primary", class: "dropdown-toggle", "data-toggle": "dropdown" },
					h(vmraid.components.FontAwesome, { type: "smile-o", fixed: true })
				),
				h("div", { class: "dropdown-menu dropdown-menu-right", onclick: e => e.stopPropagation() },
					h("div", { class: "panel panel-default" },
						h(vmraid.chat.component.EmojiPicker.List)
					)
				)
			)
		)
	}
}
vmraid.chat.component.EmojiPicker.List
=
class extends Component {
	render ( ) {
		const { props } = this

		return (
			h("div", { class: "list-group" },

			)
		)
	}
}

/**
 * @description Python equivalent to sys.platform
 */
vmraid.provide('vmraid._')
vmraid._.platform   = () => {
	const string    = navigator.appVersion

	if ( string.includes("Win") ) 	return "Windows"
	if ( string.includes("Mac") ) 	return "Darwin"
	if ( string.includes("X11") ) 	return "UNIX"
	if ( string.includes("Linux") ) return "Linux"

	return undefined
}

/**
 * @description VMRaid's Asset Helper
 */
vmraid.provide('vmraid.assets')
vmraid.assets.image = (image, app = 'vmraid') => {
	const  path     = `/assets/${app}/images/${image}`
	return path
}

/**
 * @description Notify using Web Push Notifications
 */
vmraid.provide('vmraid.boot')
vmraid.provide('vmraid.browser')
vmraid.browser.Notification = 'Notification' in window

vmraid.notify     = (string, options) => {
	vmraid.log    = vmraid.Logger.get('vmraid.notify')

	const OPTIONS = {
		icon: vmraid.assets.image('favicon.png', 'vmraid'),
		lang: vmraid.boot.lang || "en"
	}
	options       = Object.assign({ }, OPTIONS, options)

	if ( !vmraid.browser.Notification )
		vmraid.log.error('ERROR: This browser does not support desktop notifications.')

	Notification.requestPermission(status => {
		if ( status === "granted" ) {
			const notification = new Notification(string, options)
		}
	})
}

vmraid.chat.render = (render = true, force = false) =>
{
	vmraid.log.info(`${render ? "Enable" : "Disable"} Chat for User.`)

	const desk = 'desk' in vmraid
	if ( desk ) {
		// With the assumption, that there's only one navbar.
		const $placeholder = $('.navbar .vmraid-chat-dropdown')

		if ( render ) {
			$placeholder.removeClass('hidden')
		} else {
			$placeholder.addClass('hidden')
		}
	}

	// Avoid re-renders. Once is enough.
	if ( !vmraid.chatter || force ) {
		vmraid.chatter = new vmraid.Chat({
			target: desk ? '.vmraid-chat-toggle' : null
		})

		if ( render ) {
			if ( vmraid.session.user === 'Guest' && !desk ) {
				vmraid.store = vmraid.Store.get('vmraid.chat')
				var token	 = vmraid.store.get('guest_token')

				vmraid.log.info(`Local Guest Token - ${token}`)

				const setup_room = (token) =>
				{
					return new Promise(resolve => {
						vmraid.chat.room.create("Visitor", token).then(room => {
							vmraid.log.info(`Visitor Room Created: ${room.name}`)
							vmraid.chat.room.subscribe(room.name)

							var reference = room

							vmraid.chat.room.history(room.name).then(messages => {
								const  room = { ...reference, messages: messages }
								return room
							}).then(room => {
								resolve(room)
							})
						})
					})
				}

				if ( !token ) {
					vmraid.chat.website.token().then(token => {
						vmraid.log.info(`Generated Guest Token - ${token}`)
						vmraid.store.set('guest_token', token)

						setup_room(token).then(room => {
							vmraid.chatter.render({ room })
						})
					})
				} else {
					setup_room(token).then(room => {
						vmraid.chatter.render({ room })
					})
				}
			} else {
				vmraid.chatter.render()
			}
		}
	}
}

vmraid.chat.setup  = () => {
	vmraid.log     = vmraid.Logger.get('vmraid.chat')

	vmraid.log.info('Setting up vmraid.chat')
	vmraid.log.warn('TODO: vmraid.chat.<object> requires a storage.')

	if ( vmraid.session.user !== 'Guest' ) {
		// Create/Get Chat Profile for session User, retrieve enable_chat
		vmraid.log.info('Creating a Chat Profile.')

		vmraid.chat.profile.create('enable_chat').then(({ enable_chat }) => {
			vmraid.log.info(`Chat Profile created for User ${vmraid.session.user}.`)

			if ( 'desk' in vmraid && vmraid.sys_defaults ) { // same as desk?
				const should_render = Boolean(parseInt(vmraid.sys_defaults.enable_chat)) && enable_chat
				vmraid.chat.render(should_render)
			}
		})

		// Triggered when a User updates his/her Chat Profile.
		// Don't worry, enable_chat is broadcasted to this user only. No overhead. :)
		vmraid.chat.profile.on.update((user, profile) => {
			if ( user === vmraid.session.user && 'enable_chat' in profile ) {
				vmraid.log.warn(`Chat Profile update (Enable Chat - ${Boolean(profile.enable_chat)})`)
				const should_render = Boolean(parseInt(vmraid.sys_defaults.enable_chat)) && profile.enable_chat
				vmraid.chat.render(should_render)
			}
		})
	} else {
		// Website Settings
		vmraid.log.info('Retrieving Chat Website Settings.')
		vmraid.chat.website.settings(["socketio", "enable", "enable_from", "enable_to"])
			.then(settings => {
				vmraid.log.info(`Chat Website Setting - ${JSON.stringify(settings)}`)
				vmraid.log.info(`Chat Website Setting - ${settings.enable ? "Enable" : "Disable"}`)

				var should_render = settings.enable
				if ( settings.enable_from && settings.enable_to ) {
					vmraid.log.info(`Enabling Chat Schedule - ${settings.enable_from.format()} : ${settings.enable_to.format()}`)

					const range   = new vmraid.datetime.range(settings.enable_from, settings.enable_to)
					should_render = range.contains(vmraid.datetime.now())
				}

				if ( should_render ) {
					vmraid.log.info("Initializing Socket.IO")
					vmraid.socketio.init(settings.socketio.port)
				}

				vmraid.chat.render(should_render)
		})
	}
}

// TODO: Re-enable after re-designing chat
// $(document).on('ready toolbar_setup', () =>
// {
// 	vmraid.chat.setup()
// })
