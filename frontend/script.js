const API_BASE_URL = 'http://localhost:8000/api';

let currentUserId = null;
let currentUserName = null;
let isAuthenticated = false;

// ===== PAGES =====

function showPage(pageName) {
    document.querySelectorAll('.page').forEach(p => p.style.display = 'none');
    document.getElementById(pageName).style.display = 'block';

    // Manage header visibility
    if (pageName === 'mainPage') {
        if (isAuthenticated) {
            document.getElementById('authHeader').style.display = 'flex';
            document.getElementById('guestHeader').style.display = 'none';
            document.getElementById('userName').textContent = currentUserName;
        } else {
            document.getElementById('authHeader').style.display = 'none';
            document.getElementById('guestHeader').style.display = 'flex';
        }
    }
}

// ===== REGISTRATION =====

async function handleRegister() {
    const surname = document.getElementById('regSurname').value.trim();
    const name = document.getElementById('regName').value.trim();
    const password = document.getElementById('regPassword').value;
    const email = document.getElementById('regEmail').value.trim();
    const phone = document.getElementById('regPhone').value.trim();

    // Required fields: surname, name, email, password
    if (!surname || !name || !email || !password) {
        alert('Please fill in all required fields (Last Name, First Name, Email, Password)');
        return;
    }

    // Validate email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        alert('Please enter a valid email address');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                surname,
                name,
                password,
                email,
                phone: phone || null
            })
        });

        if (!response.ok) {
            const error = await response.json();
            alert(`Error: ${error.detail}`);
            return;
        }

        const userData = await response.json();
        currentUserId = userData.id;
        currentUserName = userData.name;
        isAuthenticated = true;

        // Clear form
        document.getElementById('regSurname').value = '';
        document.getElementById('regName').value = '';
        document.getElementById('regPassword').value = '';
        document.getElementById('regEmail').value = '';
        document.getElementById('regPhone').value = '';

        alert('✅ Registration successful! Welcome!');
        showPage('mainPage');
        loadEvents();
    } catch (error) {
        console.error('Error:', error);
        alert('Error: ' + error.message);
    }
}

// ===== LOGIN =====

async function handleLogin() {
    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;

    if (!email || !password) {
        alert('Please fill in all required fields');
        return;
    }

    try {
        const formData = new FormData();
        formData.append('email', email);
        formData.append('password', password);

        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            alert(`Error: ${error.detail}`);
            return;
        }

        const userData = await response.json();
        currentUserId = userData.id;
        currentUserName = userData.name;
        isAuthenticated = true;

        // Clear form
        document.getElementById('loginEmail').value = '';
        document.getElementById('loginPassword').value = '';

        showPage('mainPage');
        loadEvents();
    } catch (error) {
        console.error('Error:', error);
        alert('Error: ' + error.message);
    }
}

// ===== EVENTS =====

async function loadEvents(eventType = null) {
    try {
        let url = `${API_BASE_URL}/events`;
        if (eventType) url += `?event_type=${eventType}`;

        const response = await fetch(url);
        const events = await response.json();

        const eventsList = document.getElementById('eventsList');
        eventsList.innerHTML = '';

        if (events.length === 0) {
            eventsList.innerHTML = '<p>No available events</p>';
            return;
        }

        events.forEach(event => {
            const eventCard = document.createElement('div');
            eventCard.className = 'event-card';
            const registerBtn = isAuthenticated
                ? `<button onclick="registerForEvent(${event.id})" ${event.available_seats <= 0 ? 'disabled' : ''}>${event.available_seats > 0 ? 'Register' : 'No Seats'}</button>`
                : `<button onclick="alert('Please sign in to register for an event')">Register</button>`;

            eventCard.innerHTML = `
                <h3>${event.title}</h3>
                <p><strong>Organizer:</strong> ${event.organizer.name} ${event.organizer.surname}</p>
                <p><strong>Type:</strong> ${event.event_type}</p>
                <p><strong>Date:</strong> ${new Date(event.event_date).toLocaleString('en-US', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })}</p>
                <p><strong>Location:</strong> ${event.location}</p>
                <p><strong>Available Seats:</strong> ${event.available_seats}/${event.total_seats}</p>
                ${registerBtn}
            `;
            eventsList.appendChild(eventCard);
        });
    } catch (error) {
        console.error('Error loading events:', error);
    }
}

async function registerForEvent(eventId) {
    if (!currentUserId) {
        alert('You are not signed in');
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
            alert(`Error: ${error.detail}`);
            return;
        }

        alert('You have successfully registered for the event!');

        // ✅ ДОБАВЬ ЭТО - перезагрузи события
        loadEvents();

    } catch (error) {
        console.error('Error:', error);
        alert('Error: ' + error.message);
    }
}


async function createEvent(e) {
    // If function is called as form submit handler
    if (e && e.preventDefault) {
        e.preventDefault();
    }

    if (!currentUserId) {
        alert('You are not signed in');
        return;
    }

    const title = document.getElementById('eventTitle').value.trim();
    const description = document.getElementById('eventDescription').value.trim();
    const eventType = document.getElementById('eventType').value;
    const eventDate = document.getElementById('eventDate').value;
    const location = document.getElementById('eventLocation').value.trim();
    const totalSeats = parseInt(document.getElementById('eventSeats').value);

    if (!title || !eventType || !eventDate || !location || !totalSeats) {
        alert('Please fill in all required fields');
        return;
    }

    try {
        console.log('Sending event:', {
            title,
            description,
            event_type: eventType,
            event_date: new Date(eventDate).toISOString(),
            location,
            total_seats: totalSeats
        });

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

        console.log('Server response:', response.status);

        if (!response.ok) {
            const error = await response.json();
            console.error('Server error:', error);
            alert(`Error: ${error.detail}`);
            return;
        }

        const createdEvent = await response.json();
        console.log('Event created:', createdEvent);

        alert('✅ Event created!');

        // Clear form
        document.getElementById('createEventForm').reset();

        showPage('mainPage');
        loadEvents();
    } catch (error) {
        console.error('Error:', error);
        alert('Error creating event: ' + error.message);
    }
}

async function cancelRegistration(registrationId) {
    if (!confirm('Are you sure?')) return;

    try {
        const response = await fetch(`${API_BASE_URL}/registrations/${registrationId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            alert('Error canceling registration');
            return;
        }

        alert('✅ Registration canceled');
        loadProfileRegistrations();
        loadEvents();
    } catch (error) {
        console.error('Error:', error);
        alert('Error: ' + error.message);
    }
}

// ===== PROFILE =====

async function loadProfile() {
    if (!currentUserId) return;

    try {
        const response = await fetch(`${API_BASE_URL}/profile/${currentUserId}`);
        const user = await response.json();

        document.getElementById('profileSurname').value = user.surname;
        document.getElementById('profileName').value = user.name;
        document.getElementById('profileEmail').value = user.email || '';
        document.getElementById('profilePhone').value = user.phone || '';
        document.getElementById('profileCreatedAt').textContent = new Date(user.created_at).toLocaleString('en-US');
    } catch (error) {
        console.error('Error:', error);
    }
}

async function updateProfile() {
    if (!currentUserId) return;

    const surname = document.getElementById('profileSurname').value;
    const name = document.getElementById('profileName').value;
    const email = document.getElementById('profileEmail').value;
    const phone = document.getElementById('profilePhone').value;

    try {
        const response = await fetch(`${API_BASE_URL}/profile/${currentUserId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                surname: surname || undefined,
                name: name || undefined,
                email: email || undefined,
                phone: phone || undefined
            })
        });

        if (!response.ok) {
            const error = await response.json();
            alert(`Error: ${error.detail}`);
            return;
        }

        const updated = await response.json();
        currentUserName = updated.name;
        alert('✅ Profile updated!');
    } catch (error) {
        console.error('Error:', error);
        alert('Error: ' + error.message);
    }
}

// ===== AUTHENTICATION CHECK =====

function checkAuth(callback) {
    if (!isAuthenticated) {
        alert('Please sign in to access this feature');
        return;
    }
    callback();
}

function logout() {
    currentUserId = null;
    currentUserName = null;
    isAuthenticated = false;
    document.getElementById('authHeader').style.display = 'none';
    showPage('registerPage');
}

// ===== PROFILE - TAB NAVIGATION =====

function showProfileTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.profile-tab').forEach(tab => {
        tab.classList.remove('active');
    });

    // Remove active class from all buttons
    document.querySelectorAll('.profile-nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show the needed tab
    if (tabName === 'editProfile') {
        document.getElementById('editProfileTab').classList.add('active');
        document.querySelectorAll('.profile-nav-btn')[0].classList.add('active');
        loadProfile();
    } else if (tabName === 'myRegistrations') {
        document.getElementById('myRegistrationsTab').classList.add('active');
        document.querySelectorAll('.profile-nav-btn')[1].classList.add('active');
        loadProfileRegistrations();
    } else if (tabName === 'myEvents') {
        document.getElementById('myEventsTab').classList.add('active');
        document.querySelectorAll('.profile-nav-btn')[2].classList.add('active');
        loadProfileEvents();
    } else if (tabName === 'eventCalendar') {
        document.getElementById('eventCalendarTab').classList.add('active');
        document.querySelectorAll('.profile-nav-btn')[3].classList.add('active');
        loadEventCalendar();
    }
}

// ===== MY REGISTRATIONS IN PROFILE =====

async function loadProfileRegistrations() {
    if (!currentUserId) return;

    try {
        console.log('Loading registrations for user:', currentUserId);

        const response = await fetch(`${API_BASE_URL}/registrations/user/${currentUserId}`);

        console.log('Response:', response.status);

        if (!response.ok) {
            console.error('Response error:', response.statusText);
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const registrations = await response.json();
        console.log('Loaded registrations:', registrations);

        const registrationsList = document.getElementById('profileRegistrationsList');
        registrationsList.innerHTML = '';

        if (!registrations || registrations.length === 0) {
            registrationsList.innerHTML = '<p>You have not registered for any events</p>';
            return;
        }

        registrations.forEach(reg => {
            const regCard = document.createElement('div');
            regCard.className = 'event-card';
            regCard.innerHTML = `
                <h3>${reg.event.title}</h3>
                <p><strong>Type:</strong> ${reg.event.event_type}</p>
                <p><strong>Date:</strong> ${new Date(reg.event.event_date).toLocaleString('en-US', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })}</p>
                <p><strong>Location:</strong> ${reg.event.location}</p>
                <p><strong>Registered:</strong> ${new Date(reg.registered_at).toLocaleString('en-US')}</p>
                <button onclick="cancelRegistration(${reg.id})">Cancel Registration</button>
            `;
            registrationsList.appendChild(regCard);
        });
    } catch (error) {
        console.error('Error loading registrations:', error);
        const registrationsList = document.getElementById('profileRegistrationsList');
        if (registrationsList) {
            registrationsList.innerHTML = '<p style="color: red;">Error loading registrations</p>';
        }
    }
}

// ===== MY EVENTS IN PROFILE =====

async function loadProfileEvents() {
    if (!currentUserId) return;

    try {
        const response = await fetch(`${API_BASE_URL}/events/user/${currentUserId}`);
        const events = await response.json();

        const eventsList = document.getElementById('profileEventsList');
        eventsList.innerHTML = '';

        if (events.length === 0) {
            eventsList.innerHTML = '<p>You have not created any events</p>';
            return;
        }

        events.forEach(event => {
            const eventCard = document.createElement('div');
            eventCard.className = 'profile-event-card';
            eventCard.innerHTML = `
                <div>
                    <h4>${event.title}</h4>
                    <p><strong>Type:</strong> ${event.event_type}</p>
                    <p><strong>Date:</strong> ${new Date(event.event_date).toLocaleString('en-US', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })}</p>
                    <p><strong>Location:</strong> ${event.location}</p>
                    <p><strong>Available Seats:</strong> ${event.available_seats}/${event.total_seats}</p>
                </div>
                <div class="profile-event-actions">
                    <button onclick="editProfileEvent(${event.id})">Edit</button>
                    <button class="delete" onclick="deleteProfileEvent(${event.id})">Delete</button>
                </div>
            `;
            eventsList.appendChild(eventCard);
        });
    } catch (error) {
        console.error('Error:', error);
    }
}

// ===== EDIT EVENT =====

async function editProfileEvent(eventId) {
    if (!currentUserId) return;

    try {
        const response = await fetch(`${API_BASE_URL}/events/${eventId}`);
        const event = await response.json();

        // Fill form
        document.getElementById('editEventTitle').value = event.title;
        document.getElementById('editEventDescription').value = event.description || '';
        document.getElementById('editEventType').value = event.event_type;
        document.getElementById('editEventLocation').value = event.location;
        document.getElementById('editEventSeats').value = event.total_seats;

        // Convert date to correct format for datetime-local
        const date = new Date(event.event_date);
        const dateStr = date.toISOString().slice(0, 16);
        document.getElementById('editEventDate').value = dateStr;

        // Save event ID for later saving
        window.currentEditingEventId = eventId;

        // Show edit page
        showPage('editEventPage');
    } catch (error) {
        console.error('Error:', error);
        alert('Error loading event: ' + error.message);
    }
}

// ===== SAVE EVENT CHANGES =====

async function saveEventChanges(e) {
    if (e && e.preventDefault) {
        e.preventDefault();
    }

    if (!currentUserId || !window.currentEditingEventId) {
        alert('Error: event not loaded');
        return;
    }

    const title = document.getElementById('editEventTitle').value.trim();
    const description = document.getElementById('editEventDescription').value.trim();
    const eventType = document.getElementById('editEventType').value;
    const eventDate = document.getElementById('editEventDate').value;
    const location = document.getElementById('editEventLocation').value.trim();
    const totalSeats = parseInt(document.getElementById('editEventSeats').value);

    if (!title || !eventType || !eventDate || !location || !totalSeats) {
        alert('Please fill in all required fields');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/events/${window.currentEditingEventId}`, {
            method: 'PUT',
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
            alert(`Error: ${error.detail}`);
            return;
        }

        alert('✅ Event updated!');

        // Clear form
        document.getElementById('editEventForm').reset();
        window.currentEditingEventId = null;

        // Wait for a small delay before updating
        await new Promise(resolve => setTimeout(resolve, 500));

        // Return to profile
        showPage('profilePage');

        // Wait for page to be ready
        await new Promise(resolve => setTimeout(resolve, 100));

        showProfileTab('myEvents');

        // Load data
        await loadProfileEvents();
        await loadEvents();
    } catch (error) {
        console.error('Error:', error);
        alert('Error saving event: ' + error.message);
    }
}

// ===== DELETE EVENT =====

async function deleteProfileEvent(eventId) {
    if (!confirm('Are you sure? This action cannot be undone!')) return;

    try {
        const response = await fetch(`${API_BASE_URL}/events/${eventId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            alert('Error deleting event');
            return;
        }

        alert('✅ Event deleted!');
        loadProfileEvents();
        loadEvents(); // Update main page
    } catch (error) {
        console.error('Error:', error);
        alert('Error: ' + error.message);
    }
}

// ===== EVENT CALENDAR =====

let calendarInstance = null;

async function loadEventCalendar() {
    if (!currentUserId) return;

    try {
        // Load events the user is registered for
        const registrationsResponse = await fetch(`${API_BASE_URL}/registrations/user/${currentUserId}`);
        const registrations = await registrationsResponse.json();

        // Load events organized by the user
        const myEventsResponse = await fetch(`${API_BASE_URL}/events/user/${currentUserId}`);
        const myEvents = await myEventsResponse.json();

        // Create calendar events
        const calendarEvents = [];

        // Add events organized by the user (red)
        myEvents.forEach(event => {
            calendarEvents.push({
                title: `${event.title} (yours)`,
                start: event.event_date,
                classNames: ['event-organized'],
                backgroundColor: '#ff6b6b',
                borderColor: '#d32f2f'
            });
        });

        // Add events user is registered for (yellow)
        registrations.forEach(reg => {
            calendarEvents.push({
                title: `${reg.event.title}`,
                start: reg.event.event_date,
                classNames: ['event-registered'],
                backgroundColor: '#ffc107',
                borderColor: '#f57f17'
            });
        });

        // Destroy old calendar if it exists
        if (calendarInstance) {
            calendarInstance.destroy();
        }

        // Create new calendar
        const calendarEl = document.getElementById('calendar');
        calendarInstance = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            locale: 'en',
            headerToolbar: {
                left: 'prev,next',
                center: 'title',
                right: 'dayGridMonth,dayGridWeek'
            },
            events: calendarEvents,
            datesSet: function (info) {
                console.log('Calendar loaded');
            }
        });

        calendarInstance.render();
    } catch (error) {
        console.error('Error loading calendar:', error);
    }
}

// ===== INITIALIZATION =====

document.addEventListener('DOMContentLoaded', function () {
    // Show main page with events
    showPage('mainPage');

    // Load events (available to everyone)
    loadEvents();

    // Add handler for login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            handleLogin();
        });
    }

    // Add handler for registration form
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', (e) => {
            e.preventDefault();
            handleRegister();
        });
    }

    // Add handler for create event form
    const createEventForm = document.getElementById('createEventForm');
    if (createEventForm) {
        createEventForm.addEventListener('submit', createEvent);
    }

    // Add handler for edit event form
    const editEventForm = document.getElementById('editEventForm');
    if (editEventForm) {
        editEventForm.addEventListener('submit', saveEventChanges);
    }
});

