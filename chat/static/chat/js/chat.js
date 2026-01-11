/**
 * Sistema de Xat en Directe - JavaScript
 * Gestiona l'enviament, càrrega i eliminació de missatges amb polling
 */

document.addEventListener('DOMContentLoaded', function () {
    const chatMessages = document.getElementById('chat-messages');
    const chatForm = document.getElementById('chat-form');
    const chatErrors = document.getElementById('chat-errors');
    const messageCount = document.getElementById('message-count');

    // Només inicialitzar si existeix el contenidor de missatges
    if (!chatMessages) return;

    /**
     * Escapa caràcters HTML per prevenir XSS
     */
    function escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, char => map[char]);
    }

    /**
     * Fa scroll al final de l'àrea de missatges
     */
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    /**
     * Actualitza el comptador de missatges
     */
    function updateMessageCount(count) {
        if (messageCount) {
            messageCount.textContent = count;
        }
    }

    /**
     * Crea l'element HTML per a un missatge
     */
    function createMessageElement(message) {
        const div = document.createElement('div');
        div.className = 'chat-message' + (message.is_highlighted ? ' highlighted' : '');
        div.setAttribute('data-message-id', message.id);

        let actionsHtml = '';
        if (message.can_delete) {
            actionsHtml = `
                <div class="message-actions">
                    <button class="btn btn-sm btn-link text-danger delete-message"
                            data-message-id="${message.id}"
                            title="Eliminar missatge">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </div>
            `;
        }

        div.innerHTML = `
            <div class="message-header">
                <strong>${escapeHtml(message.display_name)}</strong>
                <small class="text-muted">${escapeHtml(message.created_at)}</small>
            </div>
            <div class="message-content">${escapeHtml(message.message)}</div>
            ${actionsHtml}
        `;

        return div;
    }

    /**
     * Carrega els missatges del servidor
     */
    async function loadMessages() {
        try {
            const response = await fetch(`/chat/${eventId}/messages/`);
            const data = await response.json();

            // Netejar el contenidor
            chatMessages.innerHTML = '';

            // Afegir cada missatge
            if (data.messages && data.messages.length > 0) {
                data.messages.forEach(msg => {
                    chatMessages.appendChild(createMessageElement(msg));
                });
            } else {
                chatMessages.innerHTML = `
                    <div class="text-center text-muted py-4">
                        <i class="fas fa-comments"></i>
                        <p class="mb-0 mt-2">No hi ha missatges encara. Sigues el primer!</p>
                    </div>
                `;
            }

            // Actualitzar comptador i fer scroll
            updateMessageCount(data.messages ? data.messages.length : 0);
            scrollToBottom();

        } catch (error) {
            console.error('Error carregant missatges:', error);
        }
    }

    /**
     * Envia un missatge nou
     */
    async function sendMessage(event) {
        event.preventDefault();

        const formData = new FormData(chatForm);
        const messageInput = chatForm.querySelector('textarea');

        // Netejar errors anteriors
        if (chatErrors) {
            chatErrors.innerHTML = '';
        }

        try {
            const response = await fetch(`/chat/${eventId}/send/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            });

            const data = await response.json();

            if (data.success) {
                // Netejar el formulari
                messageInput.value = '';
                // Recarregar missatges
                await loadMessages();
            } else {
                // Mostrar errors
                let errorHtml = '<div class="alert alert-danger alert-sm py-1 mb-0">';
                if (data.errors) {
                    for (const field in data.errors) {
                        data.errors[field].forEach(err => {
                            errorHtml += `<small>${escapeHtml(err)}</small><br>`;
                        });
                    }
                } else if (data.error) {
                    errorHtml += `<small>${escapeHtml(data.error)}</small>`;
                }
                errorHtml += '</div>';
                if (chatErrors) {
                    chatErrors.innerHTML = errorHtml;
                }
            }
        } catch (error) {
            console.error('Error enviant missatge:', error);
            if (chatErrors) {
                chatErrors.innerHTML = `
                    <div class="alert alert-danger alert-sm py-1 mb-0">
                        <small>Error de connexió. Torna-ho a provar.</small>
                    </div>
                `;
            }
        }
    }

    /**
     * Elimina un missatge
     */
    async function deleteMessage(messageId) {
        if (!confirm('Estàs segur que vols eliminar aquest missatge?')) {
            return;
        }

        try {
            // Obtenir CSRF token del formulari o de les cookies
            let csrfToken = '';
            if (chatForm) {
                const csrfInput = chatForm.querySelector('input[name="csrfmiddlewaretoken"]');
                if (csrfInput) {
                    csrfToken = csrfInput.value;
                }
            }
            // Fallback: obtenir de les cookies
            if (!csrfToken) {
                csrfToken = document.cookie.split('; ')
                    .find(row => row.startsWith('csrftoken='))
                    ?.split('=')[1] || '';
            }

            const response = await fetch(`/chat/message/${messageId}/delete/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (data.success) {
                // Recarregar missatges
                await loadMessages();
            } else {
                alert(data.error || 'No s\'ha pogut eliminar el missatge.');
            }
        } catch (error) {
            console.error('Error eliminant missatge:', error);
            alert('Error de connexió. Torna-ho a provar.');
        }
    }

    // Event listener per al formulari
    if (chatForm) {
        chatForm.addEventListener('submit', sendMessage);
    }

    // Event delegation per als botons d'eliminar
    chatMessages.addEventListener('click', function (event) {
        const deleteBtn = event.target.closest('.delete-message');
        if (deleteBtn) {
            const messageId = deleteBtn.getAttribute('data-message-id');
            deleteMessage(messageId);
        }
    });

    // Càrrega inicial de missatges
    loadMessages();

    // Polling: carregar missatges cada 3 segons
    setInterval(loadMessages, 3000);
});
