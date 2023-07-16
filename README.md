# Discord Bot to manage Voice Chat Channels

This Bot is used to create and delete Voice Channels. The main function is to create new temporary Voice Chat Channels when a user joins a `Join to create new VC` Channel.
The user that joined the creation VC will have all rights for the new Channel, when a channel is empty, it will be deleted.

In contrast to temporary, the Bot can also create permanent Channels, these will be created with `/vc_create`. 
A user has to have a specific Role to create these VCs and each User can only create one permanent Channel.
Like the temporary Channels the User that ran the command will have all the Channel rights.

## Commands

- `/vc_create` - creates a permanent Voice Chat Channel 
- `/ping` - get the Latency of the Bot

## config.py

This Bot needs a `config.js`, the file looks like this:

```py
TOKEN = 'Token'
CREATE_CHANNEL = ID
VC_CATEGORY = ID
```

- `TOKEN` has to be your Bot Token, keep in Mind, that this has to be in `''` becuase it will be used as a string.
- `CREATE_CHANNEL` is the ID of the Voice Chat Channel, that people can join to create new temporary ones.
- `VC_CATEGORY` is the is the category in which the permanent Voice Channels will be created.