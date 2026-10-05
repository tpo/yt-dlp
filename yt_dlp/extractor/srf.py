import json
import re

from .common import InfoExtractor
from ..utils import ExtractorError, unescapeHTML


class SRFIE(InfoExtractor):
    IE_DESC = 'srf.ch'
    _VALID_URL = r'https?://(?:www\.)?srf\.ch/(?!play/)(?:[^/?#]+/)*(?P<id>[^/?#]+)'
    _TESTS = [{
        # single embed via player-widget
        'url': 'https://www.srf.ch/play/radio/popupaudioplayer?id=86cd168b-04ea-3933-baac-b2e3ef4d8599',
        'info_dict': {
            'id': '86cd168b-04ea-3933-baac-b2e3ef4d8599',
            'ext': 'mp3',
            'title': 'Schulproteste in Frankreich: Was steckt hinter der Wut?',
            'duration': 733.032,
            'thumbnail': r're:^https?://download-media\.srf\.ch/.+\.jpg$',
            'timestamp': 1791207000,
            'upload_date': '20261005',
            'description': "Doch angefangen hat das Ganze \u00fcberhaupt nicht mit Sch\u00fclerprotesten, die ARD-Korrespondentin in Frankreich, Julia Borutta. Sie erkl\u00e4rt auch, wie sie die Situation erlebt und wie die Regierung nun inhaltlich auf die Forderungen reagieren will. Auch sagen Sch\u00fclerinnen und Lehrperson, weshalb sie auf die Strasse gehen.\n____________________\n\nHabt Ihr Fragen oder Themen-Inputs? Schreibt uns gerne per Mail an newsplus@srf.ch oder sendet uns eine Sprachnachricht an 076 320 10 37.\n____________________\n\nIn dieser Episode zu h\u00f6ren:\n- Julia Borutta, ARD Frankreich-Korrespondentin \n___________________\n\nTeam:\n- Moderation: Susanne St\u00f6ckl\n- Produktion: Lea Saager\n- Mitarbeit: Martina Koch \n____________________\n\nDas ist \u00abNews Plus\u00bb:\nIn einer Viertelstunde die Welt besser verstehen \u2013 ein Thema, neue Perspektiven und Antworten auf eure Fragen. Unsere Korrespondenten und Expertinnen aus der Schweiz und der Welt erkl\u00e4ren, analysieren und erz\u00e4hlen, was sie bewegt. \u00abNews Plus\u00bb von SRF erscheint immer von Montag bis Freitag um 16 Uhr rechtzeitig zum Feierabend."
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
