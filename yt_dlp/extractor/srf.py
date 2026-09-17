import json
import re

from .common import InfoExtractor
from ..utils import ExtractorError, unescapeHTML


class SRFIE(InfoExtractor):
    IE_DESC = 'srf.ch'
    _VALID_URL = r'https?://(?:www\.)?srf\.ch/(?!play/)(?:[^/?#]+/)*(?P<id>[^/?#]+)'
    _TESTS = [{
        # single embed via player-widget
        'url': 'https://www.srf.ch/news/international/kosovo-tribunal-hashim-thaci-verurteilt-wie-das-urteil-das-kosovo-veraendert',
        'info_dict': {
            'id': '388214a2-9dff-3408-87ba-c5f08c193e50',
            'ext': 'mp3',
            'title': 'Thaci wegen Kriegsverbrechen verurteilt',
            'duration': 217.656,
            'thumbnail': r're:^https?://download-media\.srf\.ch/.+\.jpg$',
            'timestamp': 1789574400,
            'upload_date': '20260916',
        },
        'params': {'skip_download': True},
    }, {
        # multiple embeds via player-widget + video-gallery
        'url': 'https://www.srf.ch/sport/fussball/super-league/nachtragsspiel-der-4-runde-4-tore-vor-der-pause-lugano-ueberfaehrt-schwache-st-galler',
        'info_dict': {
            'id': 'nachtragsspiel-der-4-runde-4-tore-vor-der-pause-lugano-ueberfaehrt-schwache-st-galler',
            'title': str,
        },
        'playlist_mincount': 2,
        'params': {'skip_download': True},
    }]

    def _extract_urns(self, webpage):
        urns = []
        for tag in re.findall(
                r'<div\b[^>]*\bdata-js-plugin="(?:player-widget|video-gallery|audio-gallery)"[^>]*>', webpage):
            m = re.search(r'\bdata-assets?="([^"]*)"', tag)
            if not m:
                continue
            raw = unescapeHTML(m.group(1)).replace('\\/', '/')
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue

            for asset in data if isinstance(data, list) else [data]:
                urn = (asset or {}).get('urn')
                if urn and urn not in urns:
                    urns.append(urn)

        return urns

    def _real_extract(self, url):
        display_id = self._match_id(url)
        webpage = self._download_webpage(url, display_id)
        urns = self._extract_urns(webpage)
        if not urns:
            raise ExtractorError('No media found', expected=True)

        entries = [
            self.url_result(urn.replace('urn:', 'srgssr:', 1), 'SRGSSR')
            for urn in urns
        ]
        if len(entries) == 1:
            return entries[0]

        return self.playlist_result(
            entries, display_id, self._og_search_title(webpage, default=None))
