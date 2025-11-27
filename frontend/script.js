const API_BASE_URL = 'http://localhost:8000/api';

let currentUserId = null;
let currentUserName = null;

// ===== СТРАНИЦЫ =====

function showPage(pageName) {
    document.querySelectorAll('.page').forEach(p => p.style.display = 'none');
    document.getElementById(pageName).style.display = 'block';
}

// ===== РЕГИСТРАЦИЯ/ВХОД =====

async function handleLogin(isRegister) {
    const surname = document.getElementById('loginSurname').value;
    const name = document.getElementById('loginName').value;
    const password = document.getElementById('loginPassword').value;
    const email = document.getElementById('loginEmail').value;
    const phone = document.getElementById('loginPhone').value;

    if (!surname || !name || !password) {
        alert('Заполните все обязательные поля');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/users`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                surname,
                name,
                password,
                email: email || null,
                phone: phone || null
            })
        });

        if (!response.ok) {
            const error = await response.json();
            alert(`Ошибка: ${error.detail}`);
            return;
        }

        const userData = await response.json();
        currentUserId = userData.id;
        currentUserName = userData.name;

        // Очищаем форму
        document.getElementById('loginSurname').value = '';
        document.getElementById('loginName').value = '';
        document.getElementById('loginPassword').value = '';
        document.getElementById('loginEmail').value = '';
        document.getElementById('loginPhone').value = '';

        showPage('mainPage');
        loadEvents();
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка при регистрации: ' + error.message);
    }
}

function toggleLoginMode() {
    const isRegister = document.getElementById('loginEmail').style.display === 'none';
    
    if (isRegister) {
        document.getElementById('loginEmail').style.display = 'block';
        document.getElementById('loginPhone').style.display = 'block';
        document.getElementById('loginBtn').textContent = 'Зарегистрироваться';
        document.getElementById('toggleModeBtn').textContent = 'Уже есть аккаунт';
    } else {
        document.getElementById('loginEmail').style.display = 'none';
        document.getElementById('loginPhone').style.display = 'none';
        document.getElementById('loginBtn').textContent = 'Войти';
        document.getElementById('toggleModeBtn').textContent = 'Создать аккаунт';
    }
}

// ===== СОБЫТИЯ =====

async function loadEvents(eventType = null) {
    try {
        let url = `${API_BASE_URL}/events`;
        if (eventType) url += `?event_type=${eventType}`;

        const response = await fetch(url);
        const events = await response.json();

        const eventsList = document.getElementById('eventsList');
        eventsList.innerHTML = '';

        if (events.length === 0) {
            eventsList.innerHTML = '<p>Нет доступных событий</p>';
            return;
        }

        events.forEach(event => {
            const eventCard = document.createElement('div');
            eventCard.className = 'event-card';
            eventCard.innerHTML = `
                <h3>${event.title}</h3>
                <p><strong>Тип:</strong> ${event.event_type}</p>
                <p><strong>Дата:</strong> ${new Date(event.event_date).toLocaleString('ru-RU')}</p>
                <p><strong>Место:</strong> ${event.location}</p>
                <p><strong>Доступных мест:</strong> ${event.available_seats}/${event.total_seats}</p>
                <button onclick="registerForEvent(${event.id})" ${event.available_seats <= 0 ? 'disabled' : ''}>
                    ${event.available_seats > 0 ? 'Зарегистрироваться' : 'Нет мест'}
                </button>
            `;
            eventsList.appendChild(eventCard);
        });
    } catch (error) {
        console.error('Ошибка при загрузке событий:', error);
        alert('Ошибка при загрузке событий');
    }
}

async function registerForEvent(eventId) {
    if (!currentUserId) {
        alert('Вы не авторизованы');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/registrations?user_id=${currentUserId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ event_id: eventId })
        });

        if (!response.ok) {
            const error = await response.json();
            alert(`Ошибка: ${error.detail}`);
            return;
        }

        alert('✅ Вы успешно зарегистрированы на событие!');
        loadEvents();
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка при регистрации: ' + error.message);
    }
}

async function createEvent() {
    const title = document.getElementById('eventTitle').value;
    const description = document.getElementById('eventDescription').value;
    const eventType = document.getElementById('eventType').value;
    const eventDate = document.getElementById('eventDate').value;
    const location = document.getElementById('eventLocation').value;
    const totalSeats = parseInt(document.getElementById('eventSeats').value);

    if (!title || !eventType || !eventDate || !location || !totalSeats) {
        alert('Заполните все обязательные поля');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/events?organizer_id=${currentUserId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title,
                description,
                event_type: eventType,
                event_date: new Date(eventDate).toISOString(),
                location,
                total_seats: totalSeats
            })
        });

        if (!response.ok) {
            const error = await response.json();
            alert(`Ошибка: ${error.detail}`);
            return;
        }

        alert('✅ Событие создано!');
        document.getElementById('eventTitle').value = '';
        document.getElementById('eventDescription').value = '';
        document.getElementById('eventType').value = 'Meetup';
        document.getElementById('eventDate').value = '';
        document.getElementById('eventLocation').value = '';
        document.getElementById('eventSeats').value = '';
        
        loadEvents();
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка при создании события: ' + error.message);
    }
}

async function loadMyRegistrations() {
    if (!currentUserId) return;

    try {
        const response = await fetch(`${API_BASE_URL}/registrations/user/${currentUserId}`);
        const registrations = await response.json();

        const registrationsList = document.getElementById('registrationsList');
        registrationsList.innerHTML = '';

        if (registrations.length === 0) {
            registrationsList.innerHTML = '<p>Вы не зарегистрированы ни на одно событие</p>';
            return;
        }

        registrations.forEach(reg => {
            const regCard = document.createElement('div');
            regCard.className = 'registration-card';
            regCard.innerHTML = `
                <h3>${reg.event.title}</h3>
                <p><strong>Дата:</strong> ${new Date(reg.event.event_date).toLocaleString('ru-RU')}</p>
                <p><strong>Место:</strong> ${reg.event.location}</p>
                <p><strong>Зарегистрирован:</strong> ${new Date(reg.registered_at).toLocaleString('ru-RU')}</p>
                <button onclick="cancelRegistration(${reg.id})">Отменить регистрацию</button>
            `;
            registrationsList.appendChild(regCard);
        });
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка при загрузке регистраций');
    }
}

async function cancelRegistration(registrationId) {
    if (!confirm('Вы уверены?')) return;

    try {
        const response = await fetch(`${API_BASE_URL}/registrations/${registrationId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            alert('Ошибка при отмене регистрации');
            return;
        }

        alert('✅ Регистрация отменена');
        loadMyRegistrations();
        loadEvents();
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка: ' + error.message);
    }
}

function logout() {
    currentUserId = null;
    currentUserName = null;
    showPage('loginPage');
}

// Инициализация
showPage('loginPage');
