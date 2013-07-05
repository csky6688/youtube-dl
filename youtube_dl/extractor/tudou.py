# coding: utf-8

import re
import json

from .common import InfoExtractor


class TudouIE(InfoExtractor):
    _VALID_URL = r'(?:http://)?(?:www\.)?tudou\.com/(?:listplay|programs|albumplay)/(?:view|(.+?))/(?:([^/]+)|([^/]+))(?:\.html)?'
    _TESTS = [{
        u'url': u'http://www.tudou.com/listplay/zzdE77v6Mmo/2xN2duXMxmw.html',
        u'file': u'2xN2duXMxmw.f4v',
        u'md5': u'140a49ed444bd22f93330985d8475fcb',
        u'info_dict': {
            u"title": u"卡马乔国足开大脚长传冲吊集锦"
        }
    },
    {
        u'url': u'http://www.tudou.com/albumplay/TenTw_JgiPM/PzsAs5usU9A.html',
        u'file': u'todo.mp4',
        u'md5': u'todo.mp4',
        u'info_dict': {
            u'title': u'todo.mp4',
        },
        u'add_ie': [u'Youku'],
        u'skip': u'Only works from China'
    }]

    def _url_for_id(self, id, quality = None):
        info_url = "http://v2.tudou.com/f?id="+str(id)
        if quality:
            info_url += '&hd' + quality
        webpage = self._download_webpage(info_url, id, "Opening the info webpage")
        final_url = self._html_search_regex('>(.+?)</f>',webpage, 'video url')
        return final_url

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group(2)
        webpage = self._download_webpage(url, video_id)

        m = re.search(r'vcode:\s*[\'"](.+?)[\'"]', webpage)
        if m and m.group(1):
            return {
                '_type': 'url',
                'url': u'youku:' + m.group(1),
                'ie_key': 'Youku'
            }

        title = self._search_regex(
            r",kw:\s*['\"](.+?)[\"']", webpage, u'title')
        thumbnail_url = self._search_regex(
            r",pic:\s*[\"'](.+?)[\"']", webpage, u'thumbnail URL', fatal=False)

        segs_json = self._search_regex(r'segs: \'(.*)\'', webpage, 'segments')
        segments = json.loads(segs_json)
        # It looks like the keys are the arguments that have to be passed as
        # the hd field in the request url, we pick the higher
        quality = sorted(segments.keys())[-1]
        segs = segments[quality]
        parts = []
        len_segs = len(segs)
        if len_segs > 1:
            self.to_screen(u'%s: found %s parts' % (video_id, len_segs))
        for part in segs:
            part_id = part['k']
            final_url = self._url_for_id(part_id, quality)
            ext = (final_url.split('?')[0]).split('.')[-1]
            parts.append(final_url)

        info_dict = {'id': video_id,
                     'ext': ext,
                     'title': title,
                     'thumbnail': thumbnail_url,
                     }
        if len_segs == 1:
            info_dict['url'] = parts[0]
        else:
            info_dict['parts'] = parts
        return info_dict
