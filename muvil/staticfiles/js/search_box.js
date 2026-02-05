    const endpoint = '{% static 'json/spain_cities.json' %}';
    const cities = [];

    fetch(endpoint)
        .then(blob => blob.json())
        .then(data => cities.push(...data));

    function findMatches(wordToMatch, cities) {
        return cities.filter(place => {
            const regex = new RegExp(wordToMatch, 'gi');
            return place.city.match(regex);
        });
    }

    function displayMatches(e) {
        const matchedArray = findMatches(e.target.value, cities);
        const html = matchedArray.map(place => {
            const regex = new RegExp(e.target.value, 'gi');
            const cityName = place.city.replace(regex,
                `<span class=hl>${e.target.value}</span>`)
            return `
                <li>
                    <span class="name">${cityName}</span>
                    <span class="people">${place.population}</span>
                </li>
            `
        }).join('');
        suggestions.innerHTML = html;
    }

    const search = document.querySelector('.search');
    const suggestions = document.querySelector('.suggestions');

    search.addEventListener('change', displayMatches);
    search.addEventListener('keyup', displayMatches);