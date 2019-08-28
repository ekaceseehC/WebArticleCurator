#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import json
from bs4 import BeautifulSoup


# BEGIN SITE SPECIFIC extract_next_page_url FUNCTIONS ##################################################################

def extract_next_page_url_444(archive_page_raw_html):
    """
        extracts and returns next page URL from an HTML code if there is one...
        Specific for 444.hu

        :returns string of url if there is one, None otherwise
    """
    ret = None
    soup = BeautifulSoup(archive_page_raw_html, 'lxml')
    next_page = soup.find(class_='infinity-next button')
    if next_page is not None and 'href' in next_page.attrs:
        ret = next_page['href']
    return ret


def extract_next_page_url_blikk(archive_page_raw_html):
    """
        extracts and returns next page URL from an HTML code if there is one...
        Specific for blikk.hu

        :returns string of url if there is one, None otherwise
    """
    ret = None
    soup = BeautifulSoup(archive_page_raw_html, 'lxml')
    next_page = soup.find(class_='archiveDayRow2')
    if next_page is not None:
        next_page_a = next_page.find('a', text='Következő oldal')
        if next_page_a is not None and 'href' in next_page_a.attrs:
            ret = 'https:{0}'.format(next_page_a['href'])
    return ret


def extract_next_page_url_mno(archive_page_raw_html):
    """
        extracts and returns next page URL from an HTML code if there is one...
        Specific for magyarnemzet.hu

        :returns string of url if there is one, None otherwise
    """
    ret = None
    soup = BeautifulSoup(archive_page_raw_html, 'lxml')
    next_page = soup.find(class_='en-navigation-line-right-arrow')
    if next_page is not None and 'href' in next_page.attrs:
        ret = next_page['href']
    return ret


def extract_next_page_url_nol(archive_page_raw_html):
    """
        extracts and returns next page URL from an HTML code if there is one...
        Specific for nol.hu

        :returns string of url if there is one, None otherwise
    """
    ret = None
    soup = BeautifulSoup(archive_page_raw_html, 'lxml')
    next_page = soup.find(class_='next')
    if next_page is not None:
        # find('a') is a must, because on the last page there is only the div and no 'a'
        # (eg. nol.hu/archivum?page=14670 )
        next_page_a = next_page.find('a')
        if next_page_a is not None and 'href' in next_page_a.attrs:
            ret = 'http://nol.hu{0}'.format(next_page_a['href'])
    return ret


def extract_next_page_url_test(filename):
    """Quick test"""

    w = WarcCachingDownloader(filename, None, Logger(), just_cache=True)

    # Some of these are intentionally yields None
    print('Testing 444')
    text = w.download_url('https://444.hu/2018/04/08')
    assert extract_next_page_url_444(text) == 'https://444.hu/2018/04/08?page=2'
    text = w.download_url('https://444.hu/2018/04/08?page=3')
    assert extract_next_page_url_444(text) is None
    text = w.download_url('https://444.hu/2013/04/13')
    assert extract_next_page_url_444(text) is None

    print('Testing nol')
    text = w.download_url('http://nol.hu/archivum?page=14668')
    assert extract_next_page_url_nol(text) == 'http://nol.hu/archivum?page=14669'
    text = w.download_url('http://nol.hu/archivum?page=14669')
    assert extract_next_page_url_nol(text) is None

    print('Testing magyarnemzet')
    text = w.download_url('https://magyarnemzet.hu/archivum/page/99643')
    assert extract_next_page_url_mno(text) == 'https://magyarnemzet.hu/archivum/page/99644/'
    text = w.download_url('https://magyarnemzet.hu/archivum/page/99644')
    assert extract_next_page_url_mno(text) is None

    print('Testing blikk')
    text = w.download_url('https://www.blikk.hu/archivum/online?date=2018-10-15')
    assert extract_next_page_url_blikk(text) == 'https://www.blikk.hu/archivum/online?date=2018-10-15&page=1'
    text = w.download_url('https://www.blikk.hu/archivum/online?date=2018-10-15&page=4')
    assert extract_next_page_url_blikk(text) is None

    print('Test OK!')


# END SITE SPECIFIC extract_next_page_url FUNCTIONS ####################################################################

# BEGIN SITE SPECIFIC extract_article_urls_from_page FUNCTIONS #########################################################

def safe_extract_hrefs_from_a_tags(main_container):
    """
    Helper function to extract href from a tags
    :param main_container: An iterator over Tag()-s
    :return: Generator over the extracted links
    """
    for a_tag in main_container:
        a_tag_a = a_tag.find('a')
        if a_tag_a is not None and 'href' in a_tag_a.attrs:
            yield a_tag_a['href']


def extract_article_urls_from_page_nol(archive_page_raw_html):
    """
        extracts and returns as a list the URLs belonging to articles from an HTML code
    :param archive_page_raw_html: archive page containing list of articles with their URLs
    :return: list that contains URLs
    """
    urls = set()
    # multi_valued_attributes=None in the Soup constructor garantees that multi-value attributes are not splitted!
    # Therefore 'vezetoCimkeAfter' is the only class element!
    # TODO: Ide kellene egy olyan, ahol tényleg probléma ez, mert szerintem nincs a middleCol-ban ilyen...
    soup = BeautifulSoup(archive_page_raw_html, 'lxml', multi_valued_attributes=None)
    main_container = soup.find_all(class_='middleCol')  # There are two of them!
    for a_tag in main_container:
        if a_tag is not None:
            a_tag_as = a_tag.find_all('a', class_='vezetoCimkeAfter')  # Here find_all()!
            for a_tag_a in a_tag_as:
                if a_tag_a is not None and 'href' in a_tag_a.attrs:
                    urls.add(a_tag_a['href'])
    return urls


def extract_article_urls_from_page_origo(archive_page_raw_html):
    """
        extracts and returns as a list the URLs belonging to articles from an HTML code
    :param archive_page_raw_html: archive page containing list of articles with their URLs
    :return: list that contains URLs
    """
    soup = BeautifulSoup(archive_page_raw_html, 'lxml')
    main_container = soup.find_all(class_='archive-cikk')
    urls = {link for link in safe_extract_hrefs_from_a_tags(main_container)}
    return urls


def extract_article_urls_from_page_444(archive_page_raw_html):
    """
        extracts and returns as a list the URLs belonging to articles from an HTML code
    :param archive_page_raw_html: archive page containing list of articles with their URLs
    :return: list that contains URLs
    """
    soup = BeautifulSoup(archive_page_raw_html, 'lxml')
    main_container = soup.find_all(class_='card')
    urls = {link for link in safe_extract_hrefs_from_a_tags(main_container)}
    return urls


def extract_article_urls_from_page_blikk(archive_page_raw_html):
    """
        extracts and returns as a list the URLs belonging to articles from an HTML code
    :param archive_page_raw_html: archive page containing list of articles with their URLs
    :return: list that contains URLs
    """
    soup = BeautifulSoup(archive_page_raw_html, 'lxml')
    main_container = soup.find_all(class_='archiveDayRow')
    urls = {link for link in safe_extract_hrefs_from_a_tags(main_container)}
    return urls


def extract_article_urls_from_page_index(archive_page_raw_html):
    """
        extracts and returns as a list the URLs belonging to articles from an HTML code
    :param archive_page_raw_html: archive page containing list of articles with their URLs
    :return: list that contains URLs
    """
    soup = BeautifulSoup(archive_page_raw_html, 'lxml')
    main_container = soup.find_all('article')
    urls = {link for link in safe_extract_hrefs_from_a_tags(main_container)}
    return urls


def extract_article_urls_from_page_mno(archive_page_raw_html):
    """
        extracts and returns as a list the URLs belonging to articles from an HTML code
    :param archive_page_raw_html: archive page containing list of articles with their URLs
    :return: list that contains URLs
    """
    soup = BeautifulSoup(archive_page_raw_html, 'lxml')
    main_container = soup.find_all('h2')
    urls = {link for link in safe_extract_hrefs_from_a_tags(main_container)}
    return urls


def extract_article_urls_from_page_valasz(archive_page_raw_html):
    """
        extracts and returns as a list the URLs belonging to articles from an HTML code
    :param archive_page_raw_html: archive page containing list of articles with their URLs
    :return: list that contains URLs
    """
    soup = BeautifulSoup(archive_page_raw_html, 'lxml')
    container = soup.find(class_='cont')
    if container is not None:
        main_container = container.find_all('article')
        urls = {'http://valasz.hu{0}'.format(link) for link in safe_extract_hrefs_from_a_tags(main_container)}
    else:
        urls = None
    return urls


def extract_article_urls_from_page_vs(archive_page_raw_html):
    """
        extracts and returns as a list the URLs belonging to articles from an HTML code
    :param archive_page_raw_html: archive page containing list of articles with their URLs
    :return: list that contains URLs
    """
    urls = set()
    my_json = json.loads(archive_page_raw_html)
    html_list = my_json['Data']['ArchiveContents']
    for html_fragment in html_list:
        for fragment in html_fragment['ContentBoxes']:
            soup = BeautifulSoup(fragment, 'lxml')
            urls.update('https://vs.hu{0}'.format(link) for link in safe_extract_hrefs_from_a_tags([soup]))
    return urls


def extract_article_urls_from_page_test(filename):
    w = WarcCachingDownloader(filename, None, Logger(), just_cache=True)

    print('Testing nol')
    text = w.download_url('http://nol.hu/archivum?page=37')
    extracted = extract_article_urls_from_page_nol(text)
    expected = {'http://nol.hu/archivum/szemelycsere_a_malev_gh_elen-1376265',
                'http://nol.hu/archivum/20130330-garancia-1376783',
                'http://nol.hu/archivum/20130330-politikus_es_kora-1376681',
                'http://nol.hu/belfold/rekord-sosem-volt-meg-ennyi-allami-vezetonk-1630907',
                'http://nol.hu/archivum/http://fsp.nolblog.hu/archives/2013/03/29/'
                'Szuletesnapi_retteges_a_Lendvay_utcaban/-1376849',
                'http://nol.hu/archivum/20130330-kassai_kerdesek-1376679',
                'http://nol.hu/archivum/20130330-kenyszeru_igen_simorra-1376787',
                'http://nol.hu/belfold/'
                'pilz-oliver-nem-akar-kormanyt-buktatni-egyuttmukodni-viszont-keptelenseg-1630901',
                'http://nol.hu/archivum/http://freeze.nolblog.hu/archives/2013/03/31/Vallomasok_Confessions/-1376909',
                'http://nol.hu/belfold/fuss-szijjarto-fuss-1630869',
                'http://nol.hu/belfold/megy-a-mazsolazas-botka-meg-a-raszorulokon-is-gunyolodott-egy-kicsit-1630861',
                'http://nol.hu/belfold/titkosszolgalat-zsarolas-sajtoszabadsag-magyarorszag-1630871',
                'http://nol.hu/belfold/a-kuria-megvedte-a-fidesz-frakcio-titkait-1630899',
                'http://nol.hu/belfold/zanka-tabor-fidesz-1630879'}
    assert (extracted, len(extracted)) == (expected, 14)

    print('Testing origo')
    text = w.download_url('https://www.origo.hu/hir-archivum/2019/20190119.html')
    extracted = extract_article_urls_from_page_origo(text)
    expected = {'https://www.origo.hu/sport/csapat/20190119-kezilabda-vilagbajnoksag-a-magyarok-vbcsoportjaban-hozta-a-'
                'kotelezot-a-sved-kezicsapat.html',
                'https://www.origo.hu/sport/csapat/20190119-noi-kosarlabda-nb-i-magabiztosan-nyert-a-'
                'cimvedo-sopron.html',
                'https://www.origo.hu/techbazis/20190119-nemetorszag-apple-qualcomm-iphone-betiltas-'
                'felrevezeto-tajekoztatas.html',
                'https://www.origo.hu/auto/20190118-te-jo-eg-hiaba-kuzdott-a-sofor-siman-lefujta-a-szel-az-utrol-a-'
                'teherautot.html',
                'https://www.origo.hu/sport/futball/20190119-labdarugas-olasz-foci-serie-a-tovabb-tart-az-inter-'
                'remalma-a-kiscsapat-ellen.html',
                'https://www.origo.hu/sport/csapat/20190119-kezilabda-harmadszor-is-nyert-a-siofok-a-noi-kezilabda-'
                'ehfkupaban.html',
                'https://www.origo.hu/nagyvilag/20190119-torokorszagban-ezrek-tuntettek-egy-ehsegsztrajkot-folytato-'
                'kepviselono-mellett.html',
                'https://www.origo.hu/itthon/20190119-kigyulladt-egy-uzlethelyiseg-mezokovesden.html',
                'https://www.origo.hu/nagyvilag/20190119-migranskaravan-usa-honduras-guatemala.html',
                'https://www.origo.hu/sport/trashtalk/20190119-gregg-popovich-edzokent-rekorder-san-antonio-spurs-'
                'nba.html',
                'https://www.origo.hu/sport/csapat/20190119-kezilabda-nb-i-megszorongattak-a-fradit-a-noi-kezilabda-nb-'
                'iben.html',
                'https://www.origo.hu/sport/egyeni/20190119-fucsovics-marton-es-babos-timea-tenisztorteneti-diadala-az-'
                'australian-openen.html',
                'https://www.origo.hu/itthon/20190119-ket-auto-karambolozott-kulcs-kozeleben-a-balesetben-harom-ember-'
                'megserult.html',
                'https://www.origo.hu/gazdasag/20190118-madoff-botrany-tortenete-piramisjatek.html',
                'https://www.origo.hu/sport/futball/20190119-bundesliga-18-fordulo-rb-leipzig-borussia-dortmund-'
                'bajnoki-osszefoglalo-gulacsi-peter.html',
                'https://www.origo.hu/itthon/20190119-tuntetes-eroszak.html',
                'https://www.origo.hu/itthon/20190119-kisorsoltak-az-otos-lotto-nyeroszamait-amivel-majdnem-'
                'ketmilliard-forintot-lehetett-nyerni.html',
                'https://www.origo.hu/teve/20190117-videon-mutatta-meg-sulyos-balesetet-a-szinesz-matt-wilson.html',
                'https://www.origo.hu/itthon/20190119-matol-visszatert-a-tel-orszagszerte-havazas-kezdodik.html',
                'https://www.origo.hu/itthon/20190119-nezopont-ellenzek-kozos-ep-lista-nagy-daniel.html',
                'https://www.origo.hu/sport/csapat/20190119-kezilabda-ferfi-vilagbajnoksag-csaszar-gabor-nyilatkozata-'
                'a-hazautazasarol.html',
                'https://www.origo.hu/sport/futball/20190119-labdarugas-angol-foci-premier-league-hetgolos-pldrama-'
                'hiaba-allt-fel-ketszer-is-a-leicester-video.html',
                'https://www.origo.hu/auto/20190117-bucsu-a-benzinmotortol-smart-eq-forfour-teszt.html',
                'https://www.origo.hu/nagyvilag/20190119-ma-delben-elkezdodott-pawel-adamowicz-fopolgarmester-temetese-'
                'lengyelorszagban-akit-egy-hete.html',
                'https://www.origo.hu/sport/futball/20190119-labdarugas-bajnokok-ligaja-tuzgolyo-elkepesztoen-nez-ki-'
                'kieseses-szakasz-uj-bllabdaja.html',
                'https://www.origo.hu/techbazis/20190117-tmobile-huawei-lopas-amerika.html',
                'https://www.origo.hu/sport/loero/20190119-sebestyen-peter-motorverseny-teljes-szezon-supersport-'
                'vilagbajnoksag-ptr-honda.html',
                'https://www.origo.hu/sport/csapat/20190119-kezilabda-ferfi-vilagbajnoksag-magyarorszag-dania-'
                'elozetes.html',
                'https://www.origo.hu/sport/egyeni/20190119-australian-open-djokovic-zverev-serene-williams-is-'
                'tizenhat-kozott.html',
                'https://www.origo.hu/itthon/20190119-a-tetejere-borult-egy-auto-kaposvaron-a-balesetben-egy-ember-'
                'serult-meg.html',
                'https://www.origo.hu/sport/futball/20190117-a-bajnoki-cim-amiert-semmit-sem-adnak-bundesliga-oszi-'
                'szezon.html',
                'https://www.origo.hu/nagyvilag/20190119-most-egy-euroert-lakast-vehet-sziciliaban.html',
                'https://www.origo.hu/teve/20190119-gorog-zita-nehezen-fogadta-el-szules-utani-uj-kulsejet-tv.html',
                'https://www.origo.hu/sport/csapat/20190119-kezilabda-ferfi-vilagbajnoksag-magyar-dan-meccs-hangulat-a-'
                'meccs-elott.html',
                'https://www.origo.hu/sport/egyeni/20190119-uszas-magyar-uszo-gyozte-le-hosszu-katinkat-antwerpenben-'
                'szilagyi-liliana.html',
                'https://www.origo.hu/sport/kozvetites/20190119-kezilabda-vilagbajnoksag-kozepdonto-magyarorszag-dania-'
                'elo-kozvetites-online.html',
                'https://www.origo.hu/techbazis/20190117-europa-felhalmozodott-iphone-keszletek-alacsony-kereslet.html',
                'https://www.origo.hu/gazdasag/20190119-felsooktatasi-felveteli-2019-apolas-es-betegellatas.html',
                'https://www.origo.hu/tudomany/20190119-a-hang-ugyan-nem-fizikai-objektum-megis-hat-ra-a-'
                'gravitacio.html',
                'https://www.origo.hu/itthon/20190119-karambol-tortent-nagykatanal.html',
                'https://www.origo.hu/techbazis/20190118-windows-10-mobile-tamogatas-megszunese.html',
                'https://www.origo.hu/itthon/20190119-keresi-a-rendorseg-az-idos-tolvajt-aki-alkoholszondat-'
                'lopott.html',
                'https://www.origo.hu/sport/egyeni/20190119-atletika-serulese-utan-gyozelemmel-tert-vissza-marton-'
                'anita.html',
                'https://www.origo.hu/itthon/20190118-ahmedh-tudta-ha-rendoroket-dobal-akkor-bortonbe-megy.html',
                'https://www.origo.hu/sport/csapat/20190119-a-veszprem-jatekosa-sterbik-arpad-ugrik-be-a-spanyol-ferfi-'
                'kezilabdavalogatotthoz-a-vbn.html',
                'https://www.origo.hu/sport/futball/20190119-la-liga-20-fordulo-real-madrid-sevilla-osszefoglalo-video-'
                'casemiro-luka-modric.html',
                'https://www.origo.hu/sport/egyeni/20190119-hosszu-katinka-cseh-laszlo-milak-kristof-majusban-'
                'budapesten-versenyez.html',
                'https://www.origo.hu/nagyvilag/20190119-tobben-meghaltak-es-megegtek-egy-mexikoi-uzemanyagvezetek-'
                'robbanasaban.html',
                'https://www.origo.hu/nagyvilag/20190119-ujabb-onkormanyzat-esett-aldozatul-a-bevandorlasparti-macroni-'
                'rezsimnek.html',
                'https://www.origo.hu/sport/laza/20190119-labdarugas-laza-nemet-foci-rb-leipzig-gulacsi-peter-hegedure-'
                'valtotta-a-kapuskesztyut.html',
                'https://www.origo.hu/sport/futball/20190119-kilencet-lott-a-psg-ebbol-nyolcat-a-felelmetes-csatartrio-'
                'cavani-mbappe-neymar.html',
                'https://www.origo.hu/itthon/20190119-hat-fot-kellett-eltavolitania-a-rendorsegnek-a-lanchidrol.html',
                'https://www.origo.hu/itthon/20190116-jobbik.html',
                'https://www.origo.hu/nagyvilag/20190119-amerikai-legicsapasok-vegeztek-tobb-mint-felszaz-szomaliai-'
                'dzsihadistaval.html',
                'https://www.origo.hu/itthon/20190119-kormanyszovivo-a-tuntetesek-az-epvalasztasi-kampany-reszet-'
                'kepezik.html',
                'https://www.origo.hu/sport/laza/20190119-elo-sportkozvetitesek-a-teveben-januar-19en-szombaton.html',
                'https://www.origo.hu/itthon/20190119-semjen-zsolt-tortenelmi-bun-a-nemet-nemzetiseg-egykori-'
                'eluldozese.html',
                'https://www.origo.hu/sport/futball/20190118-lasha-dvali-ferencvaros-edzotabor-belek-interju.html',
                'https://www.origo.hu/sport/csapat/20190119-kezilabda-ferfi-vilagbajnoksag-a-magyarorszag-dania-'
                'merkozes-osszefoglaloj.html',
                'https://www.origo.hu/gazdasag/20190117-spotify-igy-mukodik-a-bevetel-elosztasa-jogdijak.html',
                'https://www.origo.hu/itthon/20190119-ellenzeki-kepviselok-nagykepu-nyilatkozatai-es-csufos-'
                'kudarcai.html',
                'https://www.origo.hu/sport/csapat/20190119-kezilabda-ferfi-vilagbajnoksag-nyilatkozatok-a-magyar-dan-'
                'meccs-utan.html',
                'https://www.origo.hu/sport/futball/20190119-fc-sion-ferencvaros-felkeszulesi-merkozes-belek.html',
                'https://www.origo.hu/itthon/20190119-ahmed-h-idegenrendeszeti-orizet.html',
                'https://www.origo.hu/sport/futball/20190119-labdarugas-olasz-foci-serie-a-az-as-roma-kis-hijan-'
                'elszorakozta-a-ketgolos-elonyet-video.html',
                'https://www.origo.hu/techbazis/20190117-szexbotrany-ces-vibrator.html',
                'https://www.origo.hu/techbazis/20190116-samsung-galaxy-a90-128-gb-tarhely.html',
                'https://www.origo.hu/nagyvilag/20190119-migranskaravan-regisztracio-nelkul-keltek-at-illegalis-'
                'bevandorlok-a-mexikoiguatemalai-hataron.html',
                'https://www.origo.hu/sport/futball/20190119-bundesliga-18-fordulo-frankfurt-freiburg-leverkusen-'
                'monchengladbach-hannover-werder-augsburg.html',
                'https://www.origo.hu/gazdasag/20190119-felsooktatasi-felveteli-2019-gepeszmernok-szak.html',
                'https://www.origo.hu/teve/20190119-peneszes-dohos-lakasukban-almodni-sem-mert-a-palmafakrol-liptai-'
                'claudia.html',
                'https://www.origo.hu/itthon/20190119-ket-auto-karambolozott-budapesten-tobben-megserultek.html',
                'https://www.origo.hu/itthon/20190119-ma-13-eve-zuhant-le-a-szlovak-legiero-csapatszallito-gepe-hejcen-'
                'a-helyi-emlekmunel-ma-megemlekezest.html',
                'https://www.origo.hu/itthon/20190119-tuntetes-budapesten-szombaton.html',
                'https://www.origo.hu/gazdasag/20190117-igy-nez-ki-a-starbucks-kaveszentelye-balin-galeria-1.html',
                'https://www.origo.hu/itthon/20190119-lelkesz-a-vallasi-uldozesek-70-szazalekaban-kereszteny-az-'
                'aldozat.html',
                'https://www.origo.hu/sport/egyeni/20190119-babos-timea-fucsovics-marton-az-australian-openen-a-vegyes-'
                'parosban.html',
                'https://www.origo.hu/techbazis/20190118-call-of-duty-balck-ops-4-sarga-felkialtojel-bug.html',
                'https://www.origo.hu/itthon/20190119-ellenzek-tuntetes.html',
                'https://www.origo.hu/itthon/20190119-ep-baloldal-civilek-tamogatasa.html',
                'https://www.origo.hu/nagyvilag/20190119-tovabb-erosodott-a-liga-olasz-kormanypart-tamogatottsaga.html',
                'https://www.origo.hu/sport/egyeni/20190119-roger-federer-oltozo-nem-engedtek-be-australian-open.html',
                'https://www.origo.hu/sport/egyeni/20190119-asztalitenisz-world-tour-ezustermes-a-szudi-pergel-vegyes-'
                'paros.html',
                'https://www.origo.hu/sport/futball/20190119-premier-league-23-fordulo-arsenal-chelsea-bajnoki-'
                'osszefoglalo.html',
                'https://www.origo.hu/itthon/20190119-harmas-karambol-kophazanal.html',
                'https://www.origo.hu/sport/egyeni/20190119-vandortabor-jelentkezes-januar-vegetol.html',
                'https://www.origo.hu/sport/futball/20190119-labdarugas-angol-foci-solskjaer-manchestere-verhetetlen-'
                'hetgolos-dramat-nyert-a-liverpool.html',
                'https://www.origo.hu/teve/20190117-megnyert-egy-teves-vetelkedot-de-inkabb-visszamegy-a-harcterre-'
                'sophie-faldo.html',
                'https://www.origo.hu/itthon/20190119-tavaly-augusztusba-egy-vaskuti-ferfi-eletveszelyesen-megkeselt-'
                'egy-soltvadkerti-ferfit.html',
                }
    assert (extracted, len(extracted)) == (expected, 89)

    print('Testing 444')
    text = w.download_url('https://444.hu/2019/07/06')
    extracted = extract_article_urls_from_page_444(text)
    expected = {'https://444.hu/2019/07/06/azt-hiszed-szar-iroasztalod-van-nezd-meg-hova-ultettek-ursula-von-der-'
                'leyent',
                'https://444.hu/2019/07/06/kendernay-janos-lett-az-lmp-tars-nelkul-tarselnoke',
                'https://444.hu/2019/07/06/elhangzott-minden-idok-pride-ellenes-erve',
                'https://444.hu/2019/07/06/balmazujvaros-polgarmesterenek-egy-bulvarlap-szolt-hogy-eppen-atverik-oket-'
                'a-focicsapattal',
                'https://444.hu/2019/07/06/egy-nappal-kesobb-a-dk-is-csatlakozott-a-szegedi-ellenzeki-osszefogashoz',
                'https://444.hu/2019/07/06/tobb-szaz-kormanyellenes-tuntetot-vittek-el-a-rendorok-kazahsztanban',
                'https://444.hu/2019/07/06/dunaba-akart-ugrani-a-rendorok-huztak-vissza',
                'https://444.hu/2019/07/06/vaczi-zoltan-a-nyilatkozataval-futballtortenelmet-irt-az-uj-vasas-stadion-'
                'megnyitoja-utan',
                'https://444.hu/2019/07/06/az-utobbi-20-ev-legerosebb-foldrengese-razta-meg-del-kaliforniat',
                'https://444.hu/2019/07/06/lehet-hogy-meg-tobb-faval-lassithatnank-a-klimavaltozast-de-az-amazonasnal-'
                'pont-most-kapcsoltak-csucssebessegre-az-erdoirtok',
                'https://444.hu/2019/07/06/zivatarokkal-ront-az-orszagra-a-hidegfront',
                'https://444.hu/2019/07/06/letartoztattak-egy-het-orosz-titkosszolgalati-tisztbol-allo-fegyveres-'
                'rablobandat',
                'https://444.hu/2019/07/06/eves-auschwitzi-turaja-kozben-halt-meg-a-mengele-laboratoriumaban-'
                'megkinzott-hires-holokauszttulelo-de-elotte-meg-kiposztolta-a-legaranyosabb-holokauszttemaju-twitet',
                'https://444.hu/2019/07/06/cinikus-valaszt-adott-a-dk-arra-hogy-tegnap-miert-nem-alltak-be-botka-moge-'
                'ma-meg-miert-igen',
                'https://444.hu/2019/07/06/szombathely-fideszes-polgarmester-jeloltje-szerint-a-nagy-fejlesztesek-'
                'mellett-az-embereket-foglalkoztato-aprobb-dolgokra-kevesebb-figyelem-jutott',
                'https://444.hu/2019/07/06/vizi-e-szilveszter-elismerte-hogy-beszelt-palkoviccsal-az-mta-tol-elvett-'
                'kutatointezetek-vezeteserol',
                'https://444.hu/2019/07/06/remalom-kozossegi-gazdasagnak-nevezik-hogy-havi-1200-dollarert-kivehetsz-'
                'egy-agyat-egy-kimosakodott-hajlektalanszallason',
                'https://444.hu/2019/07/06/dj-snake-utan-sean-paul-is-lemondta-fellepeset-a-balaton-soundon',
                'https://444.hu/2019/07/06/kilora-vette-meg-a-hollywoodi-sztarokat-a-wall-street-farkasa-sikkasztasert-'
                'letartoztatott-producere',
                'https://444.hu/2019/07/06/fel-akarta-gyujtani-a-zsinagogat-a-balfasz-naci-sajat-magat-sikerult',
                'https://444.hu/2019/07/06/messit-kiallitottak-kakaskodasert',
                'https://444.hu/2019/07/06/lancfuresszel-faragott-vicces-szobrot-allitottak-szloveniai-szulovarosaban-'
                'melania-trumpnak',
                'https://444.hu/2019/07/06/lezarasok-lesznek-delutan-a-belvarosban-a-pride-miatt',
                'https://444.hu/2019/07/06/remiszto-hangu-leny-zaklatja-a-lakossagot-sasadon',
                'https://444.hu/2019/07/06/nem-hagyhatjuk-szo-nelkul-hogy-masodrendu-allampolgarokkent-kezeljenek-'
                'minket',
                'https://444.hu/2019/07/06/eszak-korea-szerint-kemkedett-a-letartoztatott-ausztral-diak',
                'https://444.hu/2019/07/06/kiugrott-egy-beteg-a-del-pesti-korhaz-masodik-emeleterol',
                'https://444.hu/2019/07/06/2rule-reklamot-gyartott-a-tenyek',
                'https://444.hu/2019/07/06/horvatorszag-hivatalosan-kerte-az-euro-bevezeteset',
                'https://444.hu/2019/07/06/makadon-talaltak-meg-a-hableany-utolso-elotti-aldozatat',
                'https://444.hu/2019/07/06/felhaborodtak-a-szulok-es-a-diakok-hogy-a-gyori-megyespuspok-kirugta-az-'
                'igazgatot',
                'https://444.hu/2019/07/06/a-magyar-allam-bankja-befektet-56-milliardot-meszaros-lorinc-izocukor-'
                'gyaraba',
                'https://444.hu/2019/07/06/eladja-uduloit-a-posta-hogy-legyen-penze-beremelesre',
                'https://444.hu/2019/07/06/ujabb-eros-foldrenges-razta-meg-del-kaliforniat',
                'https://444.hu/2019/07/06/havi-hatvenezres-osztondijat-kapnak-azok-az-egyetemistak-akik-hajlandok-'
                'kormanyparti-velemenyeket-irni-a-neten-az-onkormanyzati-valasztasok-elott',
                'https://444.hu/2019/07/06/durva-torlodas-alakult-ki-a-szantodi-kompnal-ezekben-a-percekben-kezd-'
                'lazulni-a-helyzet',
                'https://444.hu/2019/07/06/a-fidesz-frakciovezeto-helyettese-meg-kell-vedeni-a-gyerekeket-a-szexualis-'
                'aberraciotol-a-pride-ot-be-kell-tiltani4'
                }
    assert (extracted, len(extracted)) == (expected, 37)

    print('Testing blikk')
    text = w.download_url('https://www.blikk.hu/archivum/online?date=2018-11-13&page=0')
    extracted = extract_article_urls_from_page_blikk(text)
    expected = {'https://www.blikk.hu/aktualis/belfold/szorenyi-levente/cr10wsw',
                'https://www.blikk.hu/sztarvilag/sztarsztorik/sokk-kritika-konyhafonok-vip-sef/x7tzj86',
                'https://www.blikk.hu/sport/magyar-foci/megszolalt-merkozes-kozben-elhunyt-csornai-focista-menyasszony/'
                'ffe6ejf',
                'https://www.blikk.hu/sport/csapat/gyozelem-ferfi-vizilabda-gyozelem-oroszorszag/ewz4ql8',
                'https://www.blikk.hu/aktualis/belfold/penzvalto-rablas-motorosok-menekules-arulas-budapest/rfh8vr0',
                'https://www.blikk.hu/sport/magyar-foci/magyar-valogatott-ugrai-roland-bokaserules/96hfqer',
                'https://www.blikk.hu/sztarvilag/filmklikk/tronok-harca-uj-evead-hbo/lhvv61q',
                'https://www.blikk.hu/sztarvilag/sztarsztorik/gaspar-evelin-torta-sutes-ruzsa-magdi/5bs2fe5',
                'https://www.blikk.hu/aktualis/belfold/motorost-gazolt-halalra-egy-kamion-hodmezovasarhelynel/8mh263s',
                'https://www.blikk.hu/sztarvilag/sztarsztorik/dobo-kata-lampalaz-szineszet/f0vdqnq',
                'https://www.blikk.hu/sztarvilag/sztarsztorik/szabo-gyozo-horkolas/xrp8rcd',
                'https://www.blikk.hu/sztarvilag/sztarsztorik/a-legbatrabb-paros-kieso-cooky-sztarchat/7elsdbx',
                'https://www.blikk.hu/sztarvilag/sztarsztorik/halle-berry-marokko-szahara/g9ntm4l',
                'https://www.blikk.hu/sztarvilag/sztarsztorik/ratajkowski-bikini-napfeny/zyl4gld',
                'https://www.blikk.hu/aktualis/politika/poszony-cseh-andrej-babis/mnfhl9w',
                'https://www.blikk.hu/sztarvilag/sztarsztorik/koncert-ingyenes-hosoktere/w2lfk5q',
                'https://www.blikk.hu/aktualis/kulfold/szaud-arabia-tronorokos-szaudi-ujsagiro/y9lchkn',
                'https://www.blikk.hu/sport/kulfoldi-foci/feczesin-robert-adana-torokorszag-foci-lovoldozes/k9xj0kz',
                'https://www.blikk.hu/aktualis/belfold/idojaras-tel-egyik-naprol-a-masikra-fagyok-magyarorszag-havazas-'
                'ho/203mly4',
                'https://www.blikk.hu/aktualis/belfold/szkopje-nikola-gruevszki-macedon-miniszterelnok-budapest/'
                'dhdnknm',
                'https://www.blikk.hu/sztarvilag/sztarsztorik/stan-lee-marvel-elhunyt-felesege-halala-problemak-'
                'betegseg/b76ynlf',
                'https://www.blikk.hu/sport/kulfoldi-foci/gonzalo-higuain-ac-milan-eltiltas/h79v0dp',
                'https://www.blikk.hu/sztarvilag/sztarsztorik/r-karpati-peter-szinesz/6whxb0h',
                'https://www.blikk.hu/sport/spanyol-foci/2021-real-madrid-kispad-edzo-santaigo-solari-szerzodes/'
                'tscq598',
                'https://www.blikk.hu/aktualis/politika/rick-perry-orban-viktor-ajandek-amerika/znw4rrw',
                'https://www.blikk.hu/aktualis/belfold/diak-szex-tanarno-szekesfehervar/n3z5ljp',
                'https://www.blikk.hu/sztarvilag/sztarsztorik/vajna-timi-szexi-pucsit/2gslgww',
                'https://www.blikk.hu/sztarvilag/sztarsztorik/birsag-buntetes-autosok/x4zd3xp',
                'https://www.blikk.hu/hoppa/wtf/samsung-agyhullam-iranyitas/we73y0t',
                'https://www.blikk.hu/eletmod/egeszseg/film-cukorbetegseg-diabetesz-etkezes/35z7vws'
                }
    assert (extracted, len(extracted)) == (expected, 30)

    print('Testing index')
    text = w.download_url('https://index.hu/24ora?s=&tol=2019-07-12&ig=2019-07-12&tarskiadvanyokbanis=1&profil=&rovat='
                          '&cimke=&word=1&pepe=1&page=')
    extracted = extract_article_urls_from_page_index(text)
    expected = {'https://index.hu/mindekozben/poszt/2019/07/12/mav_korhaz_vece_vakolat_csernobil/',
                'https://index.hu/mindekozben/poszt/2019/07/12/szornyszulotteket_keszitenek_a_ketezres_evek_kedvenc_'
                'gyerekjatekabol/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_wimbledon_elodonto_legyozte_djokovic/',
                'https://index.hu/nagykep/2019/07/12/rendszervaltas_kiallitas_bankuti_andras/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/kettos_hibaval_ket_'
                'breklabdahoz_jutott_nadal/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/nadalnak_a_szettben_'
                'maradasert_kell_szervalnia/',
                'https://index.hu/belfold/2019/07/12/elhagyott_a_brfk_egy_pendrive-ot_az_osszes_munkatarsuk_szemelyes_'
                'adataval/',
                'https://index.hu/kultur/2019/07/12/egy_honap_es_jon_a_mindhunter_masodik_evada/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/szep_pontok_egymas_'
                'utan/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/elonyben_a_harmadik_'
                'szettben_a_svajci/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/ujabb_ket_breklabda/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/a_meccs_legszebb_'
                'utese_federere_de_nadal_hozta_az_adogatasat/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/15-30-cal_indult_de_'
                'hozta_federer_a_szervajat/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/4_2/',
                'https://index.hu/sport/atletika/2019/07/12/atletikai_vilagcsucs_megdolt_noi_egy_merfold_sifan_hassan_'
                'monaco_gyemant_liga/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/nadal_kiegyenlitett_a_'
                'szetteket_tekintve/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/federer_elrontotta_a_'
                'lecsapast_breklabda/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/fontos_hosszu_'
                'labdameneteket_is_nyert_federer/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/breklabdahoz_jutott_'
                'federer/',
                'https://index.hu/kultur/cinematrix/2019/07/12/leonardo_dicaprio_forrongo_jeg_ice_on_fire_'
                'dokumentumfilm_klimavaltozas/',
                'https://index.hu/belfold/2019/07/12/szombaton_visszaterhet_a_kanikula/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/megforditotta_a_'
                'svajci_megerositette_a_brekelonyt/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/nadal_haritott_egy_'
                'meccslabdat/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/magabiztosan_'
                'erositette_meg_a_breket_federer/',
                'https://index.hu/kultur/zene/2019/07/12/pataky_attila_kohaszruhaban_lepett_fel/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/nadal_emelt_a_jatekan_'
                'federer_szervaja_beragadt/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/meccslabdaja_van_'
                'federernek/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/federer_ket_labdara_'
                'nadal_szervajanal/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/ket_meccslabdarol_'
                'megforditotta_nadal/',
                'https://galeria.index.hu/sport/tenisz/2019/07/12/nadal_es_federer_meccs_wimbledon/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/sima_jatek_nadaltol/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/federer_mindketten_'
                'nagyon_magas_szinvonalon_jatszottunk/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/federer_kiharcolt_'
                'ket_breklabdat/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/masodszor_is_'
                'meccslabdaja_van_federernek/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/nadal_kezdte_a_'
                'negyedik_szettet/',
                'https://index.hu/gazdasag/2019/07/12/ujabb_allami_ceg_dobta_meg_nehany_tizmillioval_a_rogan_'
                'cecilia-fele_fitneszrendezvenyeket/',
                'https://index.hu/sport/futball/2019/07/12/antoine_griezmann_atletico_madrid_jogi_lepesek_barcelona_'
                'igazolas/',
                'https://index.hu/sport/2019/07/12/toroltek_a_red_bull_air_race_szabadedzeseinek_repuleseit/',
                'https://index.hu/kulfold/2019/07/12/papirok_nelkuli_bevandorlok_rohantak_meg_a_parizsi_pantheont/',
                'https://index.hu/techtud/2019/07/12/5_milliard_dollart_fizetne_a_facebook_hogy_elsimitsa_az_'
                'adatvedelmi_vizsgalatot/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/30-30/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/nadal_masodszor_is_'
                'lebrekelte_a_svajcit/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/federer_ujbol_semmire_'
                'hozta_a_szervajat/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/federer_egy_jatekra_'
                'a_gyozelemtol/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/semmire_szervalta_ki_'
                'federer/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/ujabb_sima_jatek_'
                'federertol/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/federer_legyozte_'
                'nadalt_12._wimbledoni_dontojebe_jutott_be/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/gyorsan_hozta_nadal_'
                'is/',
                'https://index.hu/gazdasag/2019/07/12/hol_a_penz_14_fesztival_kadar_tamas/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/nadal_egy_fonak_'
                'elutessel_haritotta/',
                'https://index.hu/gazdasag/2019/07/12/ujabb_vizsgalatok_a_johnson_johnson_ellen_a_rakkelto_hintopor_'
                'miatt/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/a_svajci_2_1_szett_'
                'melle_brekelonyben/',
                'https://divany.hu/offline/2019/07/12/szinfalak-mogotti-sztorik/',
                'https://index.hu/sport/futball/2019/07/12/szalai_adam_bundesliga_legszebb_tamadas_gol_video/',
                'https://index.hu/sport/uszas/2019/07/12/vizes_vb_2019_varakozasok_sportagak/',
                'https://index.hu/mindekozben/poszt/2019/07/12/az_amazonon_legalisan_lehet_venni_urant/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/haritotta_nadal_de_'
                'asszal_negyedik_is_van_federernek/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/federer_'
                'kiszervalhatja/',
                'https://galeria.totalcar.hu/blogok/2019/07/12/a_holdra_szallas_elozmenyei/',
                'https://index.hu/sport/tenisz/2019/07/12/federer_nadal_elodonto_wimbledon_ferfi/mindkettot_haritotta_'
                'federer/'
                }
    assert (extracted, len(extracted)) == (expected, 60)

    print('Testing velvet')
    text = w.download_url('https://velvet.hu/24ora?s=&tol=2019-08-03&ig=2019-08-04&profil=&rovat=&cimke=&word=1&pepe=1')
    extracted = extract_article_urls_from_page_index(text)
    expected = {'https://velvet.hu/nyar/2019/08/04/sziget_nagyszinpad_fellepok_heti_trend/',
                'https://velvet.hu/randi/2019/08/04/randiblog_inbox_a_felesegem_mellett_van_2_szeretom/',
                'https://velvet.hu/nyar/2019/08/04/palvin_mihalik_bikini_trend_nyar/',
                'https://velvet.hu/gumicukor/2019/08/04/megszuletett_curtisek_kisfia/',
                'https://velvet.hu/elet/2019/08/04/hawaii_kokuszposta_galeria/',
                'https://velvet.hu/gumicukor/2019/08/04/lista_nepszeru_celeb/',
                'https://velvet.hu/nyar/2019/08/04/kiegeszitok_amelyek_feldobjak_a_fesztivalszettet/',
                'https://velvet.hu/gumicukor/2019/08/04/sztarok_akik_elarultak_latvanyos_fogyasuk_titkat/',
                'https://velvet.hu/gumicukor/2019/08/03/ha_vege_a_hagyateki_'
                'targyalasnak_vajna_timea_orokre_el_akarja_hagyni_magyarorszagot/',
                'https://velvet.hu/randi/2019/08/03/randiblog_inbox_munkahelyi_szerelem/',
                'https://velvet.hu/elet/2019/08/03/megteveszto_anya-lanya_paros_galeria/',
                'https://velvet.hu/gumicukor/2019/08/03/igy_elnek_a_palyboy_villa_lanyai/',
                'https://velvet.hu/gumicukor/2019/08/03/czutor_zoltan_tapasztalatai_alapjan_'
                'tobb_a_szexista_no_mint_ferfi/',
                'https://velvet.hu/gumicukor/2019/08/03/extrem_titkos_projekt_miatt_hagyta_ott_'
                'a_radiot_sebestyen_balazs/',
                'https://velvet.hu/elet/2019/08/03/hiressegek_akik_nem_kernek_az_anyasagbol_galeria/',
                'https://velvet.hu/gumicukor/2019/08/03/mick_jagger_kisfianak_minden_rezduleseben_ott_van_az_apja/',
                'https://velvet.hu/elet/2019/08/03/27_ev_van_kozottuk_megis_boldogok_galeria/'}
    assert (extracted, len(extracted)) == (expected, 17)

    print('Testing mno')
    text = w.download_url('https://magyarnemzet.hu/archivum/page/99000/')
    extracted = extract_article_urls_from_page_mno(text)
    expected = {'https://magyarnemzet.hu/archivum/archivum-archivum/a-szuverenitas-hatarai-4473980/',
                'https://magyarnemzet.hu/archivum/archivum-archivum/tajvan-ujra-teritekre-kerult-4473983/',
                'https://magyarnemzet.hu/archivum/archivum-archivum/kie-legyen-az-iparuzesi-ado-4473989/',
                'https://magyarnemzet.hu/archivum/archivum-archivum/allampolgari-javaslatra-terveznek-furdokozpontot-'
                'gyorott-4473992/',
                'https://magyarnemzet.hu/archivum/archivum-archivum/felelem-bekes-megyeben-nappal-rendorok-ejszaka-'
                'ketes-hiru-vallalkozok-tarsai-4473998/',
                'https://magyarnemzet.hu/archivum/archivum-archivum/precedens-per-4474004/',
                'https://magyarnemzet.hu/archivum/archivum-archivum/csak-a-turelem-segithet-4473986/',
                'https://magyarnemzet.hu/archivum/archivum-archivum/kozelit-a-vilag-zagrabhoz-4473977/',
                'https://magyarnemzet.hu/archivum/archivum-archivum/tanitjak-az-onallo-eletvitelt-4474001/',
                'https://magyarnemzet.hu/archivum/archivum-archivum/veszelyforrasok-4473995/'}
    assert (extracted, len(extracted)) == (expected, 10)

    print('Testing vs')
    text = w.download_url('https://vs.hu/ajax/archive?Data={%22QueryString%22:%22%22,%22ColumnIds%22:[],'
                          '%22SubcolumnIds%22:[],%22TagIds%22:[],%22HasPublicationMinFilter%22:true,'
                          '%22PublicationMin%22:%222018-04-04T00:00:00.000Z%22,%22HasPublicationMaxFilter%22:true,'
                          '%22PublicationMax%22:%222018-04-05T00:00:00.000Z%22,%22AuthorId%22:-1,'
                          '%22MaxPublished%22:%222018-04-05T00:00:00.000Z%22,%22IsMega%22:false,%22IsPhoto%22:false,'
                          '%22IsVideo%22:false}')
    extracted = extract_article_urls_from_page_vs(text)
    expected = {'https://vs.hu/kozelet/osszes/az-lmp-is-visszalep-csepelen-0404',
                'https://vs.hu/kozelet/osszes/visszalepesek-nehany-fontos-valasztokeruletben-0404',
                'https://vs.hu/magazin/osszes/fel-evszazada-startolt-az-urodusszeia-0404',
                'https://vs.hu/gazdasag/osszes/tovabb-terjeszkedne-az-otp-bulgariaban-0404',
                'https://vs.hu/kozelet/osszes/korszerusitettek-az-elte-15-epuletet-0404',
                'https://vs.hu/magazin/osszes/kitiltjak-romaniabol-a-vekony-muanyagszatyrokat-0404',
                'https://vs.hu/kozelet/osszes/orosz-trollokat-torolt-a-facebook-0404',
                'https://vs.hu/sport/osszes/a-liverpool-es-a-barcelona-is-haromgolos-elonyben-0404',
                'https://vs.hu/kozelet/osszes/vedjegy-a-gmo-mentessegrol-0404',
                'https://vs.hu/kozelet/osszes/az-lmp-sok-csaladnak-adna-eleget-es-nem-keveseknek-sokat-0404',
                'https://vs.hu/kozelet/osszes/eros-szel-es-kellemes-homerseklet-0404',
                'https://vs.hu/kozelet/osszes/czegledy-letartoztatasanak-meghosszabbitasat-inditvanyoztak-0404',
                'https://vs.hu/kozelet/osszes/meg-szombaton-is-agital-a-fidesz-0404',
                'https://vs.hu/gazdasag/osszes/a-kopint-tarki-4-szazalekos-gdp-bovulest-var-0404',
                'https://vs.hu/kozelet/osszes/a-szkripal-ugy-a-hideghaborura-emlekeztet-0404',
                'https://vs.hu/kozelet/osszes/foldosztas-ukrajnaban-0404',
                'https://vs.hu/magazin/osszes/rendbe-hozzak-a-nadasdladanyi-kastelyt-0404',
                'https://vs.hu/kozelet/osszes/nezopont-orban-nepszerusege-folyamatosan-no-0404',
                'https://vs.hu/magazin/osszes/komaromba-koltoztetik-a-szepmuveszeti-egy-reszet-0404'
                }
    assert (extracted, len(extracted)) == (expected, 19)

    print('Testing valasz')
    text = w.download_url('http://valasz.hu/itthon/?page=1')
    extracted = extract_article_urls_from_page_valasz(text)
    expected = {'http://valasz.hu/itthon/ez-nem-autopalya-epites-nagyinterju-palinkas-jozseffel-a-tudomany-penzeirol-'
                '129168',
                'http://valasz.hu/itthon/itt-a-madaras-adidas-eletkepes-lehet-e-egy-nemzeti-sportmarka-129214',
                'http://valasz.hu/itthon/halapenzt-reszletre-129174',
                'http://valasz.hu/itthon/buda-gardens-ugy-lazar-verengzest-rendezett-a-miniszterelnoksegen-129175',
                'http://valasz.hu/itthon/minden-szinvonalat-alulmul-palinkas-jozsef-a-kormanymedia-tamadasarol-129173',
                'http://valasz.hu/itthon/szeressuk-a-szarkakat-129223',
                'http://valasz.hu/itthon/borokai-gabor-a-2rule-rol-129172',
                'http://valasz.hu/itthon/megsem-tiltottak-ki-a-belvarosbol-a-segwayeket-ez-tortent-valojaban-129222',
                'http://valasz.hu/itthon/a-heti-valasz-lap-es-konyvkiado-szolgaltato-kft-kozlemenye-129225',
                'http://valasz.hu/itthon/az-megvan-hogy-meleghazassag-es-migracioellenes-az-lmp-uj-elnoke-129211',
                'http://valasz.hu/itthon/a-nehezfiuknak-is-van-szive-129179',
                'http://valasz.hu/itthon/humboldt-dijas-kvantumfizikus-alapkutatas-nelkul-nincs-fejlodes-129197',
                'http://valasz.hu/itthon/hogyan-zajlik-egy-kereszteny-hetvege-a-fegyintezetekben-129165',
                'http://valasz.hu/itthon/ha-tetszik-ha-nem-ez-lehet-2019-sztorija-orban-vagy-macron-129201',
                'http://valasz.hu/itthon/abszurdra-sikerult-az-uj-gyulekezesi-torveny-borton-jarhat-gyurcsany-'
                'kifutyuleseert-129207'}
    assert (extracted, len(extracted)) == (expected, 15)
    print('Test OK!')

# END SITE SPECIFIC extract_article_urls_from_page FUNCTIONS ###########################################################


def extend_warc_archive_with_urls(old_warc_filename, new_warc_fineame, new_urls):
    w = WarcCachingDownloader(old_warc_filename, new_warc_fineame, Logger())
    for url in w.url_index:  # Copy all old URLs
        w.download_url(url)
    for url in new_urls:
        print('Adding url {0}'.format(url))
        w.download_url(url)


if __name__ == '__main__':
    import sys
    from os.path import dirname, join as os_path_join, abspath

    # To be able to run it standalone from anywhere!
    project_dir = abspath(os_path_join(dirname(__file__), '..'))
    sys.path.append(project_dir)
    from corpusbuilder.utils import Logger
    from corpusbuilder.enhanced_downloader import WarcCachingDownloader

    choices = {'nextpage': os_path_join(project_dir, 'tests/next_page_url.warc.gz'),
               'archive': os_path_join(project_dir, 'tests/extract_article_urls_from_page.warc.gz')}

    if len(sys.argv) > 1:
        # Usage: [echo URL|cat urls.txt] | __file__ [archive|nextpage] new.warc.gz
        warc = sys.argv[1]
        warc_filename = sys.argv[2]
        if warc not in choices.keys():
            print('ERROR: Argument must be in {0} instead of {1} and filename must supplied !'.
                  format(str(set(choices.keys())), warc))
            exit(1)
        print('Addig URLs to {0} :'.format(warc))
        input_urls = (url.strip() for url in sys.stdin)
        extend_warc_archive_with_urls(choices[warc], warc_filename, input_urls)
        print('Done!')
        print('Do not forget to mv {0} {1} before commit!'.format(warc_filename, choices[warc]))
    else:
        extract_next_page_url_test(choices['nextpage'])
        extract_article_urls_from_page_test(choices['archive'])