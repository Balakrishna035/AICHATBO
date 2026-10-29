/* script.js - Real-Time Streaming, Persistent Previous Chats History & Expandable Thinking UI */

document.addEventListener("DOMContentLoaded", () => {
    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");
    const messagesContainer = document.getElementById("messages-container");
    const engineBadge = document.getElementById("engine-badge");
    const modelPill = document.getElementById("model-pill");
    const clearBtn = document.getElementById("clear-btn");
    const newChatBtn = document.getElementById("new-chat-btn");
    const sessionIndicator = document.getElementById("session-indicator");
    const chatHistoryList = document.getElementById("chat-history-list");
    const clearAllChatsBtn = document.getElementById("clear-all-chats-btn");

    // Track active thread/session ID
    let currentThreadId = getOrCreateThreadId();
    updateSessionDisplay();

    // Load initial metadata and previous chats list
    fetchAgentMetadata();
    loadPreviousChatsList(true); // true = load most recent conversation if present

    // Chat form submit listener
    chatForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const message = userInput.value.trim();
        if (!message) return;

        handleSendStreamMessage(message);
        userInput.value = "";
    });

    // Clear visible chat display
    clearBtn.addEventListener("click", () => {
        renderWelcomeMessage("Chat display cleared. Type any constitutional query to continue.");
    });

    // New conversation: generates a fresh thread ID & clears view
    newChatBtn.addEventListener("click", () => {
        startNewConversation();
    });

    // Clear all stored chats
    if (clearAllChatsBtn) {
        clearAllChatsBtn.addEventListener("click", async () => {
            if (confirm("Are you sure you want to clear all previous chat history?")) {
                try {
                    await fetch("/api/chats", { method: "DELETE" });
                    startNewConversation();
                    loadPreviousChatsList(false);
                } catch (e) {
                    console.error("Failed to clear chat history:", e);
                }
            }
        });
    }

    function getOrCreateThreadId() {
        let tid = sessionStorage.getItem("law_thread_id");
        if (!tid) {
            tid = "chat_" + Date.now() + "_" + Math.floor(Math.random() * 1000);
            sessionStorage.setItem("law_thread_id", tid);
        }
        return tid;
    }

    function updateSessionDisplay() {
        if (sessionIndicator) {
            sessionIndicator.textContent = currentThreadId.slice(-6);
        }
    }

    function startNewConversation() {
        currentThreadId = "chat_" + Date.now() + "_" + Math.floor(Math.random() * 1000);
        sessionStorage.setItem("law_thread_id", currentThreadId);
        updateSessionDisplay();
        highlightActiveChatInSidebar(null);
        renderWelcomeMessage("Started a fresh conversation session. How can I assist you with Constitutional Law today?");
    }

    function renderWelcomeMessage(customNotice) {
        messagesContainer.innerHTML = `
            <div class="message-wrapper bot">
                <div class="avatar">🏛️</div>
                <div class="message-bubble">
                    <div class="message-content">
                        ${customNotice ? `<p class="notice-pill">${customNotice}</p>` : ""}
                        <p><strong>Namaste!</strong> I am your specialized <strong>Constitutional Law AI Agent</strong>.</p>
                        <p>Powered by <strong>LangGraph</strong>, I execute a structured legal reasoning pipeline: searching verified statutory texts, fetching landmark Supreme Court case laws, and analyzing constitutional doctrines in real time.</p>
                        <p>💡 <em>Ask about any Article (e.g. 14, 19, 21, 32), Landmark Case (Kesavananda, Maneka Gandhi, Puttaswamy), or Constitutional Writ!</em></p>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Fetch agent capabilities and database stats
     */
    async function fetchAgentMetadata() {
        try {
            const res = await fetch("/tools");
            if (res.ok) {
                const data = await res.json();
                if (engineBadge) engineBadge.textContent = "Online";
                if (modelPill) modelPill.textContent = "Legal AI Agent";
            }
        } catch (err) {
            if (engineBadge) engineBadge.textContent = "Offline Mode";
        }
    }

    /**
     * Loads previous chats list from the server
     */
    async function loadPreviousChatsList(shouldLoadLatest = false) {
        if (!chatHistoryList) return;

        try {
            const res = await fetch("/api/chats");
            if (!res.ok) return;

            const data = await res.json();
            const chats = data.chats || [];

            if (chats.length === 0) {
                chatHistoryList.innerHTML = `<div class="empty-history">No previous chats yet</div>`;
                return;
            }

            chatHistoryList.innerHTML = "";
            chats.forEach(chat => {
                const item = document.createElement("div");
                item.className = `history-item ${chat.id === currentThreadId ? 'active' : ''}`;
                item.dataset.id = chat.id;
                item.title = chat.title;

                item.innerHTML = `
                    <div class="history-item-content">
                        <span class="history-item-icon">💬</span>
                        <span class="history-item-title">${escapeHtml(chat.title)}</span>
                    </div>
                    <button type="button" class="history-item-delete" title="Delete chat">✕</button>
                `;

                // Click to load chat conversation
                item.querySelector(".history-item-content").addEventListener("click", () => {
                    loadChatConversation(chat.id);
                });

                // Delete single chat
                item.querySelector(".history-item-delete").addEventListener("click", (e) => {
                    e.stopPropagation();
                    deleteChatSession(chat.id);
                });

                chatHistoryList.appendChild(item);
            });

            // Automatically open the most recent chat on first load if currentThreadId matches or if fresh session
            if (shouldLoadLatest && chats.length > 0) {
                const targetId = chats.some(c => c.id === currentThreadId) ? currentThreadId : chats[0].id;
                loadChatConversation(targetId);
            }

        } catch (err) {
            console.warn("Could not load previous chats list:", err);
        }
    }

    /**
     * Loads full conversation for a selected chat ID
     */
    async function loadChatConversation(chatId) {
        try {
            const res = await fetch(`/api/chats/${chatId}`);
            if (!res.ok) return;

            const data = await res.json();
            const chat = data.chat;
            if (!chat) return;

            currentThreadId = chatId;
            sessionStorage.setItem("law_thread_id", currentThreadId);
            updateSessionDisplay();
            highlightActiveChatInSidebar(chatId);

            // Render all historical messages
            messagesContainer.innerHTML = "";
            const messages = chat.messages || [];

            if (messages.length === 0) {
                renderWelcomeMessage();
                return;
            }

            messages.forEach(msg => {
                if (msg.role === "user") {
                    appendUserMessage(msg.content);
                } else if (msg.role === "bot") {
                    renderRestoredBotMessage(msg);
                }
            });

            scrollToBottom();

        } catch (err) {
            console.error("Error loading chat conversation:", err);
        }
    }

    /**
     * Renders a saved bot message with its completed thinking steps accordion
     */
    function renderRestoredBotMessage(msg) {
        const wrapper = document.createElement("div");
        wrapper.className = "message-wrapper bot";

        const steps = msg.steps || [];
        const duration = msg.duration || 1.2;
        let thinkingHtml = "";

        if (steps.length > 0) {
            const stepsHtml = steps.map(s => {
                const stageIcons = {
                    "reasoning": "💭",
                    "searching": "🔍",
                    "fetching_data": "⚡",
                    "executing_tool": "🛠️",
                    "analyzing_results": "⚖️",
                    "generating_response": "📝"
                };
                const icon = stageIcons[s.stage] || "⚙️";
                const toolTag = s.tool_name ? `
                    <div class="step-tool-tag">
                        <span class="tool-label">Tool:</span> <code>${escapeHtml(s.tool_name)}(${escapeHtml(JSON.stringify(s.tool_input || {}))})</code>
                    </div>
                ` : "";
                const outputTag = s.tool_output ? `
                    <div class="step-output-box">
                        <span class="output-label">Observation:</span>
                        <pre><code>${escapeHtml(String(s.tool_output).slice(0, 300))}</code></pre>
                    </div>
                ` : "";

                return `
                    <div class="step-item stage-${s.stage}">
                        <div class="step-icon">${icon}</div>
                        <div class="step-content">
                            <div class="step-top-row">
                                <span class="step-badge ${(s.badge || 'info').toLowerCase().replace(/\s+/g, '-')}">${escapeHtml(s.badge || 'Step')}</span>
                                <span class="step-title">${escapeHtml(s.title || '')}</span>
                                <span class="step-duration">${s.duration ? s.duration + 's' : ''}</span>
                            </div>
                            <div class="step-details">${escapeHtml(s.details || '')}</div>
                            ${toolTag}
                            ${outputTag}
                        </div>
                    </div>
                `;
            }).join("");

            thinkingHtml = `
                <div class="agent-thinking-card completed">
                    <div class="thinking-header" title="Click to view or hide agent execution steps">
                        <div class="thinking-header-left">
                            <span class="thinking-check-icon">✓</span>
                            <span class="thinking-title">Thought for ${duration}s</span>
                            <span class="thinking-separator">·</span>
                            <span class="thinking-activity">${steps.length} execution steps completed</span>
                        </div>
                        <div class="thinking-header-right">
                            <span class="step-count-badge">${steps.length} steps</span>
                            <button type="button" class="thinking-toggle-btn">
                                <span class="toggle-text">Show details</span>
                                <svg class="chevron" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                                    <polyline points="6 9 12 15 18 9"></polyline>
                                </svg>
                            </button>
                        </div>
                    </div>
                    <div class="thinking-progress-track">
                        <div class="thinking-progress-bar" style="width: 100%;"></div>
                    </div>
                    <div class="thinking-steps-body">
                        ${stepsHtml}
                    </div>
                </div>
            `;
        }

        wrapper.innerHTML = `
            <div class="avatar">🏛️</div>
            <div class="message-bubble">
                ${thinkingHtml}
                <div class="message-content">
                    ${formatLegalMarkdown(msg.content)}
                </div>
            </div>
        `;

        // Attach toggle listener to thinking header
        const thinkingHeader = wrapper.querySelector(".thinking-header");
        if (thinkingHeader) {
            thinkingHeader.addEventListener("click", () => {
                const card = wrapper.querySelector(".agent-thinking-card");
                toggleThinkingCard(card);
            });
        }

        messagesContainer.appendChild(wrapper);
    }

    /**
     * Deletes a single chat session
     */
    async function deleteChatSession(chatId) {
        try {
            await fetch(`/api/chats/${chatId}`, { method: "DELETE" });
            if (currentThreadId === chatId) {
                startNewConversation();
            }
            loadPreviousChatsList(false);
        } catch (err) {
            console.error("Failed to delete chat:", err);
        }
    }

    function highlightActiveChatInSidebar(chatId) {
        const items = document.querySelectorAll(".history-item");
        items.forEach(el => {
            if (chatId && el.dataset.id === chatId) {
                el.classList.add("active");
            } else {
                el.classList.remove("active");
            }
        });
    }

    /**
     * Primary Streaming Request Handler
     */
    async function handleSendStreamMessage(message) {
        // 1. Render User Message
        appendUserMessage(message);
        scrollToBottom();

        // 2. Create the Bot Message Container with ChatGPT-style Thinking Component
        const botBubbleElements = createBotThinkingMessage();
        const { wrapper, thinkingCard, thinkingHeader, activityText, toggleBtn, stepCountBadge, progressBar, stepsBody, contentEl } = botBubbleElements;
        messagesContainer.appendChild(wrapper);
        scrollToBottom();

        // Execution tracking state
        const recordedSteps = [];
        let accumulatedText = "";
        let isCompleted = false;

        try {
            // 3. Initiate SSE Streaming Request to Flask
            const response = await fetch("/chat/stream", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: message, thread_id: currentThreadId })
            });

            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}: Failed to reach chat stream.`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");
            let buffer = "";

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split("\n\n");
                buffer = lines.pop();

                for (const line of lines) {
                    const trimmed = line.trim();
                    if (!trimmed.startsWith("data:")) continue;

                    const jsonStr = trimmed.replace(/^data:\s*/, "");
                    try {
                        const event = JSON.parse(jsonStr);
                        handleStreamEvent(event, {
                            thinkingCard,
                            activityText,
                            toggleBtn,
                            stepCountBadge,
                            progressBar,
                            stepsBody,
                            contentEl,
                            recordedSteps,
                            onToken: (chunk) => {
                                accumulatedText += chunk;
                                contentEl.innerHTML = formatLegalMarkdown(accumulatedText) + '<span class="streaming-cursor"></span>';
                                scrollToBottom();
                            },
                            onDone: (duration, totalSteps) => {
                                isCompleted = true;
                                finishThinkingUI(thinkingCard, thinkingHeader, activityText, toggleBtn, duration, totalSteps);
                                contentEl.innerHTML = formatLegalMarkdown(accumulatedText);
                                scrollToBottom();
                                // Refresh Previous Chats sidebar to show updated title and order
                                loadPreviousChatsList(false);
                            }
                        });
                    } catch (parseErr) {
                        console.warn("JSON parse error on SSE event:", parseErr, jsonStr);
                    }
                }
            }

            if (!isCompleted) {
                finishThinkingUI(thinkingCard, thinkingHeader, activityText, toggleBtn, 1.2, recordedSteps.length);
                contentEl.innerHTML = formatLegalMarkdown(accumulatedText);
                loadPreviousChatsList(false);
            }

        } catch (err) {
            console.error("Stream error:", err);
            activityText.innerHTML = `<span class="err-text">⚠️ Stream Interrupted: ${escapeHtml(err.message)}</span>`;
            progressBar.style.width = "100%";
            progressBar.classList.add("error");
            contentEl.innerHTML = `<div class="error-notice">⚠️ Error processing request: ${escapeHtml(err.message)}<br><small>Tip: Verify Flask server is running at http://127.0.0.1:5000</small></div>`;
        }

        scrollToBottom();
    }

    /**
     * Handles each parsed SSE event from LangGraph
     */
    function handleStreamEvent(event, ctx) {
        const { thinkingCard, activityText, toggleBtn, stepCountBadge, progressBar, stepsBody, recordedSteps, onToken, onDone } = ctx;

        if (event.type === "status") {
            activityText.textContent = event.status_text;
            const stageProgress = {
                "reasoning": "20%",
                "searching": "40%",
                "fetching_data": "65%",
                "analyzing_results": "85%",
                "generating_response": "96%"
            };
            if (stageProgress[event.stage]) {
                progressBar.style.width = stageProgress[event.stage];
            }
        }
        else if (event.type === "step") {
            const step = event.step;
            recordedSteps.push(step);
            stepCountBadge.textContent = `${recordedSteps.length} step${recordedSteps.length > 1 ? 's' : ''}`;
            renderStepItem(step, stepsBody);
            scrollToBottom();
        }
        else if (event.type === "token") {
            onToken(event.content);
        }
        else if (event.type === "done") {
            progressBar.style.width = "100%";
            onDone(event.duration, event.total_steps || recordedSteps.length);
        }
        else if (event.type === "error") {
            activityText.innerHTML = `<span class="err-text">⚠️ ${escapeHtml(event.message)}</span>`;
        }
    }

    /**
     * Creates Bot Message element with thinking component
     */
    function createBotThinkingMessage() {
        const wrapper = document.createElement("div");
        wrapper.className = "message-wrapper bot";

        const cardId = "thinking-" + Date.now();

        wrapper.innerHTML = `
            <div class="avatar">🏛️</div>
            <div class="message-bubble">
                <div class="agent-thinking-card running" id="${cardId}">
                    <div class="thinking-header" title="Click to view or hide agent execution steps">
                        <div class="thinking-header-left">
                            <span class="thinking-spinner"></span>
                            <span class="thinking-title">Thinking</span>
                            <span class="thinking-separator">·</span>
                            <span class="thinking-activity">Initializing LangGraph agent pipeline...</span>
                        </div>
                        <div class="thinking-header-right">
                            <span class="step-count-badge">0 steps</span>
                            <button type="button" class="thinking-toggle-btn">
                                <span class="toggle-text">Details</span>
                                <svg class="chevron" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                                    <polyline points="6 9 12 15 18 9"></polyline>
                                </svg>
                            </button>
                        </div>
                    </div>
                    <div class="thinking-progress-track">
                        <div class="thinking-progress-bar" style="width: 10%;"></div>
                    </div>
                    <div class="thinking-steps-body"></div>
                </div>

                <div class="message-content">
                    <span class="streaming-cursor"></span>
                </div>
            </div>
        `;

        const thinkingCard = wrapper.querySelector(".agent-thinking-card");
        const thinkingHeader = wrapper.querySelector(".thinking-header");
        const activityText = wrapper.querySelector(".thinking-activity");
        const toggleBtn = wrapper.querySelector(".thinking-toggle-btn");
        const stepCountBadge = wrapper.querySelector(".step-count-badge");
        const progressBar = wrapper.querySelector(".thinking-progress-bar");
        const stepsBody = wrapper.querySelector(".thinking-steps-body");
        const contentEl = wrapper.querySelector(".message-content");

        thinkingHeader.addEventListener("click", () => {
            toggleThinkingCard(thinkingCard);
        });

        return { wrapper, thinkingCard, thinkingHeader, activityText, toggleBtn, stepCountBadge, progressBar, stepsBody, contentEl };
    }

    function toggleThinkingCard(card) {
        const isExpanded = card.classList.contains("expanded");
        if (isExpanded) {
            card.classList.remove("expanded");
            const toggleText = card.querySelector(".toggle-text");
            if (toggleText) toggleText.textContent = "Show details";
        } else {
            card.classList.add("expanded");
            const toggleText = card.querySelector(".toggle-text");
            if (toggleText) toggleText.textContent = "Hide";
        }
    }

    function finishThinkingUI(card, header, activityText, toggleBtn, duration, totalSteps) {
        card.classList.remove("running");
        card.classList.add("completed");

        const spinner = card.querySelector(".thinking-spinner");
        if (spinner) {
            spinner.className = "thinking-check-icon";
            spinner.innerHTML = "✓";
        }

        const titleEl = card.querySelector(".thinking-title");
        if (titleEl) {
            titleEl.textContent = `Thought for ${duration}s`;
        }

        if (activityText) {
            activityText.textContent = `${totalSteps} execution steps completed`;
        }

        const toggleText = card.querySelector(".toggle-text");
        if (toggleText) {
            toggleText.textContent = "Show details";
        }

        card.classList.remove("expanded");
    }

    function renderStepItem(step, container) {
        const stepDiv = document.createElement("div");
        stepDiv.className = `step-item stage-${step.stage}`;

        const stageIcons = {
            "reasoning": "💭",
            "searching": "🔍",
            "fetching_data": "⚡",
            "executing_tool": "🛠️",
            "analyzing_results": "⚖️",
            "generating_response": "📝"
        };
        const icon = stageIcons[step.stage] || "⚙️";

        let toolHtml = "";
        if (step.tool_name) {
            const argStr = step.tool_input ? JSON.stringify(step.tool_input) : "{}";
            toolHtml = `
                <div class="step-tool-tag">
                    <span class="tool-label">Tool:</span> <code>${escapeHtml(step.tool_name)}(${escapeHtml(argStr)})</code>
                </div>
            `;
        }

        let outputHtml = "";
        if (step.tool_output) {
            const outStr = typeof step.tool_output === "string" ? step.tool_output : JSON.stringify(step.tool_output);
            outputHtml = `
                <div class="step-output-box">
                    <span class="output-label">Observation:</span>
                    <pre><code>${escapeHtml(outStr.slice(0, 300))}${outStr.length > 300 ? '...' : ''}</code></pre>
                </div>
            `;
        }

        stepDiv.innerHTML = `
            <div class="step-icon">${icon}</div>
            <div class="step-content">
                <div class="step-top-row">
                    <span class="step-badge ${(step.badge || 'info').toLowerCase().replace(/\s+/g, '-')}">${escapeHtml(step.badge || 'Step')}</span>
                    <span class="step-title">${escapeHtml(step.title || '')}</span>
                    <span class="step-duration">${step.duration ? step.duration + 's' : ''}</span>
                </div>
                <div class="step-details">${escapeHtml(step.details || "")}</div>
                ${toolHtml}
                ${outputHtml}
            </div>
        `;

        container.appendChild(stepDiv);
    }

    function appendUserMessage(text) {
        const wrapper = document.createElement("div");
        wrapper.className = "message-wrapper user";
        wrapper.innerHTML = `
            <div class="avatar">👤</div>
            <div class="message-bubble">
                <div class="message-content">
                    <p>${escapeHtml(text)}</p>
                </div>
            </div>
        `;
        messagesContainer.appendChild(wrapper);
    }

    function formatLegalMarkdown(raw) {
        if (!raw) return "";
        let text = escapeHtml(raw);

        text = text.replace(/^###\s+(.*$)/gim, '<h3 class="legal-h3">$1</h3>');
        text = text.replace(/^##\s+(.*$)/gim, '<h2 class="legal-h2">$1</h2>');
        text = text.replace(/^#\s+(.*$)/gim, '<h1 class="legal-h1">$1</h1>');
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
        text = text.replace(/`([^`]+)`/g, '<code class="legal-code">$1</code>');
        text = text.replace(/^\>\s+(.*$)/gim, '<blockquote class="legal-quote">$1</blockquote>');
        text = text.replace(/^[•\-\*]\s+(.*$)/gim, '<li class="legal-li">$1</li>');
        text = text.replace(/(<li class="legal-li">.*<\/li>)/gim, '<ul class="legal-ul">$1</ul>');

        const paragraphs = text.split("\n\n").map(p => {
            const trimmed = p.trim();
            if (!trimmed) return "";
            if (trimmed.startsWith("<h") || trimmed.startsWith("<ul") || trimmed.startsWith("<block")) {
                return trimmed;
            }
            return `<p>${trimmed.replace(/\n/g, "<br>")}</p>`;
        });

        return paragraphs.join("");
    }

    function escapeHtml(str) {
        if (!str) return "";
        const div = document.createElement("div");
        div.textContent = String(str);
        return div.innerHTML;
    }

    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    window.sendQuickPrompt = function(promptText) {
        userInput.value = promptText;
        chatForm.dispatchEvent(new Event("submit"));
    };
});
