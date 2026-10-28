from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import urllib.request
import random
import urllib.parse
import json

app = FastAPI(title="Cinéflix - Streaming Pro", version="7.30")
templates = Jinja2Templates(directory="templates")

TMDB_API_KEY = "264fac9bf2abf8c206d1dac490046efc"

MOVIE_GENRES = [
    {"name": "Action", "id": 28},
    {"name": "Comédie", "id": 35},
    {"name": "Drame", "id": 18},
    {"name": "Science-Fiction", "id": 878},
    {"name": "Horreur", "id": 27},
    {"name": "Animation", "id": 16},
    {"name": "Thriller", "id": 53},
    {"name": "Aventure", "id": 12}
]

TV_GENRES = [
    {"name": "Action & Adventure", "id": 10759},
    {"name": "Comédie", "id": 35},
    {"name": "Drame", "id": 18},
    {"name": "Sci-Fi & Fantasy", "id": 10765},
    {"name": "Mystère", "id": 9648},
    {"name": "Animation", "id": 16},
    {"name": "Crime", "id": 80}
]

SAGA_IDS = [
    {"id": 1241, "name": "Harry Potter"},
    {"id": 86311, "name": "Avengers / Marvel"},
    {"id": 10, "name": "Star Wars"},
    {"id": 9485, "name": "Fast & Furious"},
    {"id": 119, "name": "Le Seigneur des Anneaux"},
    {"id": 263, "name": "Batman (Dark Knight)"},
    {"id": 556, "name": "Spider-Man"},
    {"id": 295, "name": "Pirates des Caraïbes"},
    {"id": 328, "name": "Jurassic Park"},
    {"id": 562, "name": "Die Hard"},
    {"id": 234, "name": "Matrix"},
    {"id": 84, "name": "Indiana Jones"},
    {"id": 8650, "name": "Terminator"},
    {"id": 748, "name": "X-Men"},
    {"id": 645, "name": "James Bond (007)"},
    {"id": 10194, "name": "Toy Story"},
    {"id": 2150, "name": "Saw"},
    {"id": 8091, "name": "Alien"},
    {"id": 131635, "name": "Hunger Games"},
    {"id": 335, "name": "Mission Impossible"},
    {"id": 264, "name": "Retour vers le futur"}
]

def fetch_tmdb(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Erreur API TMDB ({url}): {e}")
        return {}

def render_horizontal_row(items, item_type="movie", row_id="row"):
    cards_html = ""
    for item in items:
        title = item.get("title") or item.get("name", "Titre indisponible")
        poster_path = item.get("poster_path")
        backdrop_path = item.get("backdrop_path")
        item_id = item.get("id")
        
        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
            backdrop_url = f"https://image.tmdb.org/t/p/original{backdrop_path}" if backdrop_path else poster_url
            link = f"/watch?id={item_id}&type={item_type}"
            
            cards_html += f"""
            <a href="{link}" class="movie-card" data-backdrop="{backdrop_url}" onmouseover="updateBackground(this)">
                <img src="{poster_url}" alt="{title}" loading="lazy">
                <div class="movie-title">{title}</div>
            </a>
            """
            
    if not cards_html:
        return "<p style='color: var(--text-muted); padding-left: 20px;'>Aucun contenu disponible pour le moment.</p>"

    return f"""
    <div class="row-wrapper">
        <button class="scroll-btn left-btn" onclick="scrollRow('{row_id}', -1)">❮</button>
        <div class="horizontal-row" id="{row_id}">
            {cards_html}
        </div>
        <button class="scroll-btn right-btn" onclick="scrollRow('{row_id}', 1)">❯</button>
    </div>
    """

def render_pagination(base_url, current_page, total_pages):
    if total_pages <= 1:
        return ""
    prev_page = max(1, current_page - 1)
    next_page = min(total_pages, current_page + 1)
    prev_disabled = "opacity: 0.3; pointer-events: none;" if current_page == 1 else ""
    next_disabled = "opacity: 0.3; pointer-events: none;" if current_page >= total_pages else ""
    separator = "&" if "?" in base_url else "?"

    return f"""
    <div style="display: flex; justify-content: center; align-items: center; gap: 20px; margin: 60px 0;">
        <a href="{base_url}{separator}page={prev_page}" class="page-btn" style="{prev_disabled}">Précédent</a>
        <span style="color: var(--text-muted); font-weight: 600; font-size: 0.95rem;">Page {current_page} / {total_pages}</span>
        <a href="{base_url}{separator}page={next_page}" class="page-btn" style="{next_disabled}">Suivant</a>
    </div>
    <style>
        .page-btn {{ padding: 12px 28px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); color: white; border-radius: 10px; text-decoration: none; font-weight: 600; font-size: 0.95rem; backdrop-filter: blur(10px); transition: all 0.25s ease; }}
        .page-btn:hover {{ background: var(--primary); border-color: var(--primary); box-shadow: 0 4px 20px rgba(229,9,20,0.4); transform: translateY(-2px); }}
    </style>
    """

@app.get("/", response_class=HTMLResponse)
def home(request: Request, q: str = None, genre: int = None):
    movie_row = ""
    tv_row = ""
    hero_slides = ""
    hero_dots = ""
    genre_row = ""
    trending_movies_row = ""
    trending_tv_row = ""
    selected_genre_name = ""

    if q:
        encoded_q = urllib.parse.quote(q)
        movie_data = fetch_tmdb(f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&language=fr-FR&query={encoded_q}")
        tv_data = fetch_tmdb(f"https://api.themoviedb.org/3/search/tv?api_key={TMDB_API_KEY}&language=fr-FR&query={encoded_q}")
        movie_row = render_horizontal_row(movie_data.get('results', []), 'movie', 'search_movies')
        tv_row = render_horizontal_row(tv_data.get('results', []), 'tv', 'search_tv')
    else:
        if genre is not None:
            for g in MOVIE_GENRES:
                if g["id"] == genre:
                    selected_genre_name = g["name"]
            movies_data = fetch_tmdb(f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=fr-FR&with_genres={genre}&sort_by=popularity.desc")
            genre_row = render_horizontal_row(movies_data.get('results', []), 'movie', 'genreMoviesRow')
        else:
            trending_movies = fetch_tmdb(f"https://api.themoviedb.org/3/trending/movie/day?api_key={TMDB_API_KEY}&language=fr-FR").get('results', [])
            trending_tv = fetch_tmdb(f"https://api.themoviedb.org/3/trending/tv/day?api_key={TMDB_API_KEY}&language=fr-FR").get('results', [])
            
            for idx, movie in enumerate(trending_movies[:5]):
                m_id = movie.get("id")
                title = movie.get("title", "Titre")
                overview = movie.get("overview", "Aucun synopsis disponible.")
                backdrop = movie.get("backdrop_path")
                backdrop_url = f"https://image.tmdb.org/t/p/original{backdrop}" if backdrop else ""
                vote = round(movie.get("vote_average", 0), 1)
                year = movie.get("release_date", "2026")[:4]
                active_class = "active" if idx == 0 else ""
                
                hero_slides += f"""
                <div class="hero-slide {active_class}" style="background-image: url('{backdrop_url}');">
                    <div class="hero-gradient"></div>
                    <div class="hero-content">
                        <div class="hero-badges">
                            <span class="badge film">FILM</span>
                            <span class="badge year">📅 {year}</span>
                            <span class="badge rating">⭐ {vote} / 10</span>
                        </div>
                        <h1>{title}</h1>
                        <p>{overview}</p>
                        <div class="hero-actions">
                            <a href="/watch?id={m_id}&type=movie" class="btn-play">▶ Regarder</a>
                            <a href="/watch?id={m_id}&type=movie" class="btn-info">ℹ Plus d'infos</a>
                        </div>
                    </div>
                </div>
                """
                hero_dots += f"""<span class="dot {active_class}" onclick="currentSlide({idx + 1})"></span>"""

            trending_movies_row = render_horizontal_row(trending_movies, 'movie', 'trendingMoviesRow')
            trending_tv_row = render_horizontal_row(trending_tv, 'tv', 'trendingTvRow')

    return templates.TemplateResponse(request, "index.html", {
        "active_tab": "home",
        "search_query": q if q else "",
        "movie_genres": MOVIE_GENRES,
        "current_genre": genre,
        "selected_genre_name": selected_genre_name,
        "movie_row": movie_row,
        "tv_row": tv_row,
        "hero_slides": hero_slides,
        "hero_dots": hero_dots,
        "genre_row": genre_row,
        "trending_movies_row": trending_movies_row,
        "trending_tv_row": trending_tv_row
    })

@app.get("/movies", response_class=HTMLResponse)
def movies_page(request: Request, genre: int = None, page: int = 1):
    selected_genre_name = "Films Populaires"
    for g in MOVIE_GENRES:
        if genre == g["id"]:
            selected_genre_name = f"Films : {g['name']}"

    if genre is not None:
        data = fetch_tmdb(f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=fr-FR&with_genres={genre}&sort_by=popularity.desc&page={page}")
        total_pages = min(data.get('total_pages', 1), 500)
        base_url = f"/movies?genre={genre}"
        movies_row = render_horizontal_row(data.get('results', []), 'movie', 'movieGenreRow')
    else:
        data = fetch_tmdb(f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=fr-FR&page={page}")
        total_pages = min(data.get('total_pages', 1), 500)
        base_url = "/movies"
        movies_row = render_horizontal_row(data.get('results', []), 'movie', 'popularMoviesRow')

    pagination_html = render_pagination(base_url, page, total_pages)

    return templates.TemplateResponse(request, "movies.html", {
        "active_tab": "movies",
        "search_query": "",
        "movie_genres": MOVIE_GENRES,
        "current_genre": genre,
        "page_title": selected_genre_name,
        "movies_row": movies_row,
        "pagination_html": pagination_html
    })

@app.get("/series", response_class=HTMLResponse)
def series_page(request: Request, genre: int = None, page: int = 1):
    selected_genre_name = "Séries Populaires"
    for g in TV_GENRES:
        if genre == g["id"]:
            selected_genre_name = f"Séries : {g['name']}"

    if genre is not None:
        data = fetch_tmdb(f"https://api.themoviedb.org/3/discover/tv?api_key={TMDB_API_KEY}&language=fr-FR&with_genres={genre}&sort_by=popularity.desc&page={page}")
        total_pages = min(data.get('total_pages', 1), 500)
        base_url = f"/series?genre={genre}"
        series_row = render_horizontal_row(data.get('results', []), 'tv', 'tvGenreRow')
    else:
        data = fetch_tmdb(f"https://api.themoviedb.org/3/tv/popular?api_key={TMDB_API_KEY}&language=fr-FR&page={page}")
        total_pages = min(data.get('total_pages', 1), 500)
        base_url = "/series"
        series_row = render_horizontal_row(data.get('results', []), 'tv', 'popularTvRow')

    pagination_html = render_pagination(base_url, page, total_pages)

    return templates.TemplateResponse(request, "series.html", {
        "active_tab": "series",
        "search_query": "",
        "tv_genres": TV_GENRES,
        "current_genre": genre,
        "page_title": selected_genre_name,
        "series_row": series_row,
        "pagination_html": pagination_html
    })

@app.get("/sagas", response_class=HTMLResponse)
def sagas_page(request: Request, saga: int = None):
    selected_saga_name = "Sagas Phares"
    sagas_content = ""

    if saga is not None:
        for s in SAGA_IDS:
            if s["id"] == saga:
                selected_saga_name = f"Saga : {s['name']}"
        data = fetch_tmdb(f"https://api.themoviedb.org/3/collection/{saga}?api_key={TMDB_API_KEY}&language=fr-FR")
        parts = data.get("parts", [])
        if parts:
            parts = sorted(parts, key=lambda x: x.get('release_date', '9999'))
        sagas_content = render_horizontal_row(parts, 'movie', 'sagaSelectedRow')
    else:
        main_sagas = [1241, 86311, 10, 9485, 119, 556]
        rows_html = ""
        for idx, s_id in enumerate(main_sagas):
            saga_obj = next((s for s in SAGA_IDS if s["id"] == s_id), None)
            if saga_obj:
                data = fetch_tmdb(f"https://api.themoviedb.org/3/collection/{s_id}?api_key={TMDB_API_KEY}&language=fr-FR")
                parts = data.get("parts", [])
                if parts:
                    parts = sorted(parts, key=lambda x: x.get('release_date', '9999'))
                    rows_html += f"<h2>{saga_obj['name']}</h2>"
                    rows_html += render_horizontal_row(parts, 'movie', f"saga_row_{idx}")
        sagas_content = rows_html

    return templates.TemplateResponse(request, "sagas.html", {
        "active_tab": "sagas",
        "search_query": "",
        "saga_list": SAGA_IDS,
        "current_saga": saga,
        "page_title": selected_saga_name,
        "sagas_content": sagas_content
    })

@app.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request):
    return templates.TemplateResponse(request, "profile.html", {
        "active_tab": "profile",
        "search_query": ""
    })

@app.get("/watch", response_class=HTMLResponse)
def watch(request: Request, id: int, type: str = "movie", season: int = 1, episode: int = 1):
    url = f"https://api.themoviedb.org/3/{type}/{id}?api_key={TMDB_API_KEY}&language=fr-FR"
    item = fetch_tmdb(url)
    
    credits_data = fetch_tmdb(f"https://api.themoviedb.org/3/{type}/{id}/credits?api_key={TMDB_API_KEY}&language=fr-FR")
    cast_list = credits_data.get("cast", [])[:12]

    videos_data = fetch_tmdb(f"https://api.themoviedb.org/3/{type}/{id}/videos?api_key={TMDB_API_KEY}&language=fr-FR")
    results = videos_data.get("results", [])
    if not results:
        videos_data = fetch_tmdb(f"https://api.themoviedb.org/3/{type}/{id}/videos?api_key={TMDB_API_KEY}")
        results = videos_data.get("results", [])

    trailer_key = ""
    for vid in results:
        if vid.get("site") == "YouTube" and vid.get("type") in ["Trailer", "Teaser"]:
            trailer_key = vid.get("key")
            break
    if not trailer_key:
        for vid in results:
            if vid.get("site") == "YouTube":
                trailer_key = vid.get("key")
                break

    rec_data = fetch_tmdb(f"https://api.themoviedb.org/3/{type}/{id}/recommendations?api_key={TMDB_API_KEY}&language=fr-FR")
    recommendations = rec_data.get("results", [])

    title = item.get("title") or item.get("name", "Titre")
    overview = item.get("overview", "Aucun synopsis disponible.")
    vote = round(item.get("vote_average", 0), 1)
    release = item.get("release_date") or item.get("first_air_date", "Inconnue")
    backdrop = item.get("backdrop_path")
    backdrop_url = f"https://image.tmdb.org/t/p/original{backdrop}" if backdrop else ""
    poster_path = item.get("poster_path")
    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""
    safe_title = title.replace('"', '\\"')

    selectors_html = ""
    frembed_url = ""
    vidzy_url = ""

    if type == "tv":
        frembed_url = f"https://frembed.uno/embed/serie/{id}?sa={season}&epi={episode}"
        vidzy_url = f"https://vidzy.org/tv/{id}/{season}/{episode}"
        
        seasons = item.get("seasons", [])
        seasons_options = ""
        for s in seasons:
            s_num = s.get("season_number")
            if s_num >= 0:
                s_name = s.get("name", f"Saison {s_num}")
                selected = "selected" if s_num == season else ""
                seasons_options += f'<option value="{s_num}" {selected}>{s_name}</option>'
        
        season_data = fetch_tmdb(f"https://api.themoviedb.org/3/tv/{id}/season/{season}?api_key={TMDB_API_KEY}&language=fr-FR")
        episodes = season_data.get("episodes", [])
        episodes_options = ""
        for ep in episodes:
            ep_num = ep.get("episode_number")
            ep_name = ep.get("name", f"Épisode {ep_num}")
            selected = "selected" if ep_num == episode else ""
            episodes_options += f'<option value="{ep_num}" {selected}>Ép. {ep_num} - {ep_name}</option>'
        
        next_episode = episode + 1
        selectors_html = f"""
        <div style="background: rgba(17,17,21,0.85); backdrop-filter: blur(12px); padding: 18px 24px; border-radius: 14px; margin-bottom: 25px; display: inline-block; border: 1px solid var(--border-color);">
            <form method="get" action="/watch" style="display: flex; gap: 20px; align-items: center; flex-wrap: wrap;">
                <input type="hidden" name="id" value="{id}">
                <input type="hidden" name="type" value="tv">
                <div>
                    <label style="color: var(--text-muted); margin-right: 8px; font-weight: 600; font-size: 0.9rem;">Saison :</label>
                    <select name="season" onchange="this.form.submit()" style="padding: 10px 14px; background: #050507; color: white; border: 1px solid var(--border-color); border-radius: 8px; outline: none; cursor: pointer; font-weight: 600;">
                        {seasons_options}
                    </select>
                </div>
                <div>
                    <label style="color: var(--text-muted); margin-right: 8px; font-weight: 600; font-size: 0.9rem;">Épisode :</label>
                    <select name="episode" onchange="this.form.submit()" style="padding: 10px 14px; background: #050507; color: white; border: 1px solid var(--border-color); border-radius: 8px; outline: none; cursor: pointer; font-weight: 600;">
                        {episodes_options}
                    </select>
                </div>
                <a href="/watch?id={id}&type=tv&season={season}&episode={next_episode}" style="padding: 10px 20px; background: var(--primary); color: white; border-radius: 8px; text-decoration: none; font-weight: bold; transition: all 0.2s; display: inline-block; box-shadow: 0 4px 15px rgba(229,9,20,0.3);">Épisode suivant</a>
            </form>
        </div>
        """
    else:
        frembed_url = f"https://frembed.uno/embed/movie/{id}"
        vidzy_url = f"https://vidzy.org/movie/{id}"
        selectors_html = ""

    cast_html = ""
    for actor in cast_list:
        actor_name = actor.get("name", "")
        character = actor.get("character", "")
        profile = actor.get("profile_path")
        profile_url = f"https://image.tmdb.org/t/p/w200{profile}" if profile else "https://via.placeholder.com/150?text=No+Photo"
        cast_html += f"""
        <div style="flex: 0 0 135px; text-align: center; background: var(--card-bg); border-radius: 12px; overflow: hidden; padding-bottom: 12px; border: 1px solid var(--border-color); box-shadow: 0 8px 20px rgba(0,0,0,0.4); transition: transform 0.3s ease;">
            <img src="{profile_url}" alt="{actor_name}" style="width: 100%; height: 165px; object-fit: cover;" loading="lazy">
            <div style="font-size: 0.85rem; font-weight: 700; padding: 10px 6px 2px 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{actor_name}</div>
            <div style="font-size: 0.75rem; color: var(--text-muted); padding: 0 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{character}</div>
        </div>
        """

    trailer_modal_html = ""
    if trailer_key:
        trailer_modal_html = f"""
        <div id="trailerModal" style="display: none; position: fixed; inset: 0; background: rgba(5,5,7,0.9); z-index: 2000; justify-content: center; align-items: center; backdrop-filter: blur(16px);">
            <div style="position: relative; width: 85%; max-width: 1050px; aspect-ratio: 16/9; background: #000; border-radius: 16px; overflow: hidden; box-shadow: 0 25px 60px rgba(0,0,0,0.9); border: 1px solid var(--border-color);">
                <button onclick="closeTrailer()" style="position: absolute; top: 15px; right: 15px; z-index: 2010; background: rgba(5,5,7,0.8); border: 1px solid var(--border-color); color: white; width: 42px; height: 42px; border-radius: 50%; font-size: 1.2rem; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s;">✕</button>
                <iframe id="trailerFrame" src="https://www.youtube.com/embed/{trailer_key}" style="width: 100%; height: 100%; border: none;" allow="autoplay; fullscreen" allowfullscreen></iframe>
            </div>
        </div>
        <script>
            function openTrailer() {{
                document.getElementById('trailerModal').style.display = 'flex';
            }}
            function closeTrailer() {{
                document.getElementById('trailerModal').style.display = 'none';
                let iframe = document.getElementById('trailerFrame');
                iframe.src = iframe.src;
            }}
        </script>
        """

    similar_section = ""
    if recommendations:
        similar_section = f"""
        <div style="max-width: 1500px; margin: 60px auto 40px auto; padding: 0 40px;">
            <h2>Vous aimerez aussi</h2>
            {render_horizontal_row(recommendations, type, 'recommendationsRow')}
        </div>
        """

    return templates.TemplateResponse(request, "watch.html", {
        "id": id,
        "type": type,
        "season": season,
        "episode": episode,
        "title": title,
        "safe_title": safe_title,
        "overview": overview,
        "vote": vote,
        "release": release,
        "backdrop_url": backdrop_url,
        "poster_url": poster_url,
        "selectors_html": selectors_html,
        "frembed_url": frembed_url,
        "vidzy_url": vidzy_url,
        "cast_html": cast_html,
        "trailer_key": trailer_key,
        "trailer_modal_html": trailer_modal_html,
        "similar_section": similar_section
    })
@app.get("/random")
async def random_media():
    candidates = []
    try:
        endpoints = ["trending/movie/day", "trending/tv/day", "movie/popular", "tv/popular"]
        for endpoint in endpoints:
            data = tmdb_request(endpoint)
            if data and isinstance(data, dict) and "results" in data:
                for item in data["results"]:
                    media_type = "tv" if "tv" in endpoint or "name" in item else "movie"
                    candidates.append({"id": item["id"], "type": media_type})
    except Exception as e:
        print(f"Erreur API TMDB random: {e}")
        
    # Si l'API TMDB ne renvoie rien, on pioche dans une liste de secours variée
    if not candidates:
        fallback_list = [
            {"id": 157336, "type": "movie"}, # Interstellar
            {"id": 27205, "type": "movie"},  # Inception
            {"id": 550, "type": "movie"},    # Fight Club
            {"id": 1396, "type": "tv"},      # Breaking Bad
            {"id": 66732, "type": "tv"},     # Stranger Things
            {"id": 1399, "type": "tv"},      # Game of Thrones
            {"id": 299536, "type": "movie"}, # Avengers: Infinity War
            {"id": 680, "type": "movie"},    # Pulp Fiction
            {"id": 122, "type": "movie"},    # Le Seigneur des Anneaux : Le Retour du Roi
            {"id": 238, "type": "movie"}     # Le Parrain
        ]
        chosen = random.choice(fallback_list)
        return RedirectResponse(url=f"/watch?id={chosen['id']}&type={chosen['type']}", status_code=303)
        
    # Sinon, on prend un choix aléatoire parmi les vraies données TMDB
    unique_candidates = [dict(t) for t in {tuple(d.items()) for d in candidates}]
    chosen = random.choice(unique_candidates)
    return RedirectResponse(url=f"/watch?id={chosen['id']}&type={chosen['type']}", status_code=303)

@app.get("/stats", response_class=HTMLResponse)
async def stats_page(request: Request):
    return templates.TemplateResponse(request, "stats.html", {})
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)