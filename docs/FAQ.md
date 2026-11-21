<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
# FAQ

[Home](Home.md) › FAQ

**Is this made by YouTube, Google, ModRetro, Analogue or Jellyfin?** No. ChromaTube is an independent project, not
affiliated with or endorsed by any of them. YouTube is a trademark of Google LLC.

**Is it allowed by YouTube?** No: tools that reach videos outside YouTube's own apps conflict with its Terms of
Service, and the Chromatic cannot show YouTube's official player. Setting it up is your own choice for private use
([Before you start](Before-you-start.md)).

**Why does it need my Jellyfin server?** The console cannot decode YouTube's video (H.264, VP9, AV1). Jellyfin
converts each video into the small MJPEG picture and ADPCM sound the console plays, exactly as for films.

**Does it download videos?** No. Only tiny `.strm` entries are written; a video is fetched while it plays.

**Can I search all of YouTube?** No. Only the channels in your list, their newest videos.

**Do I need a Google account, cookies or an API key?** No, and never add them.

**Does it change my Jellyfin server?** One library is added (with a backup, a dry run and proof that nothing else
changed). The container cannot change Jellyfin at all: it has no key and none of Jellyfin's files.

**Will the library show in my other Jellyfin apps?** Yes, like any library, for users who may see it. You can hide it
per user in Jellyfin.

**Why can't I seek?** Seeking in these remote videos is not proven on the console, so ChromaTube plays one stream
from the beginning.

**It worked yesterday and today nothing plays.** YouTube changes things now and then; see [Updating](Updating.md).

**Does it work on the Analogue Pocket?** Not supported.

**What does it cost?** Nothing. A few KB of disk per video listed, and one light conversion while you watch.

Next: [Building and testing](Building-and-testing.md)
