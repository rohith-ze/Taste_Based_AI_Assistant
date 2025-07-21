document.addEventListener('DOMContentLoaded', initMovies);
function initMovies() {
  fetch('/api/movies/watched').then(r => r.json()).then(renderWatched);
  fetch('/api/movies/recommended').then(r => r.json()).then(renderRecommended);
}

function renderWatched(movies) {
  let dom = document.getElementById('watched-list');
  movies.forEach(m => dom.appendChild(createMovieCard(m, true)));
}

function renderRecommended(movies) {
  let dom = document.getElementById('recommended-list');
  movies.forEach(m => dom.appendChild(createMovieCard(m, false)));
}

function createMovieCard(m, isWatched) {
  let card = document.createElement('div');
  card.className = 'card';
  card.innerHTML = `<h3>${m.name}</h3><p>${m.genres?.join(', ')}</p>`;
  if (!isWatched) {
    let btn = document.createElement('button');
    btn.textContent = 'Watch';
    btn.onclick = () => playMovie(m.id);
    card.appendChild(btn);
  }
  return card;
}

function playMovie(itemId) {
  fetch(`/api/movies/url/${itemId}`).then(r => r.json()).then(data => {
    const modal = document.getElementById('video-modal');
    document.getElementById('emby-player').src = data.playUrl;
    modal.style.display = 'flex';
    modal.querySelector('.close-btn').onclick = () => {
      document.getElementById('emby-player').src = '';
      modal.style.display = 'none';
    };
  });
}
