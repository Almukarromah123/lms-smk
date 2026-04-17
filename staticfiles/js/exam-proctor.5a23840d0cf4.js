/**
 * Exam Proctoring Protection
 * Mencegah siswa membuka tab lain, menggunakan developer tools, copy-paste, dll
 */

(function() {
    'use strict';

    const ExamProctor = {
        // Configuration
        config: {
            sessionId: null,
            enableFullscreen: true,
            enableDevToolDetection: true,
            enableCopyPasteBlock: true,
            enableRightClickBlock: true,
            enableTabSwitchDetection: true,
            enableWarnings: true,
            maxTabSwitches: 3,
            warningMessage: '⚠️ Peringatan: Anda sedang mengerjakan ujian. Membuka tab lain atau meninggalkan halaman dapat mengakibatkan ujian dibatalkan!',
            tabSwitchWarning: 'Anda sudah membuka tab lain {times} kali. Jika ini terjadi lagi, ujian dapat dibatalkan. Fokus pada ujian!'
        },

        // State tracking
        state: {
            tabSwitchCount: 0,
            isTabActive: true,
            isFullscreen: false,
            devToolsDetected: false,
            sessionStartTime: null,
            violations: []
        },

        /**
         * Initialize exam protection
         */
        init: function(sessionId) {
            this.config.sessionId = sessionId;
            this.state.sessionStartTime = new Date();

            // Setup protections only if exam is in progress
            const isExamInProgress = document.querySelector('[data-exam-status]')?.getAttribute('data-exam-status') === 'IN_PROGRESS';
            if (!isExamInProgress) return;

            console.log('🔒 Exam Protection Activated');

            // Setup all protections
            this.setupTabSwitchDetection();
            this.setupPageUnloadProtection();
            this.setupCopyPasteBlocking();
            this.setupRightClickBlocking();
            this.setupDevToolsDetection();
            this.setupFullscreenPrompt();
            this.setupKeyboardShortcuts();
            this.setupInactivityWarning();

            // Show initial warning
            if (this.config.enableWarnings) {
                this.showWarning(this.config.warningMessage, 'info', 5000);
            }

            // Log violation on page unload
            window.addEventListener('beforeunload', () => {
                if (isExamInProgress) {
                    this.logViolation('page_unload');
                }
            });
        },

        /**
         * Detect tab/window switching
         */
        setupTabSwitchDetection: function() {
            if (!this.config.enableTabSwitchDetection) return;

            document.addEventListener('visibilitychange', () => {
                const isHidden = document.hidden;

                if (isHidden) {
                    // Tab switched away from exam
                    this.state.tabSwitchCount++;
                    this.logViolation('tab_switch');

                    const message = `⚠️ Tab Switch Detected! (${this.state.tabSwitchCount}/${this.config.maxTabSwitches})`;
                    this.showWarning(message, 'error', 3000);

                    // Check if max violations reached
                    if (this.state.tabSwitchCount >= this.config.maxTabSwitches) {
                        this.showCriticalWarning(
                            'UJIAN DIBATALKAN',
                            `Anda telah membuka tab lain ${this.config.maxTabSwitches} kali. Ujian akan dibatalkan.`,
                            () => this.cancelExam()
                        );
                    }
                } else {
                    // Tab switched back to exam
                    this.state.isTabActive = true;
                    console.log('✓ Back to exam window');
                }
            });

            // Monitor window focus
            window.addEventListener('blur', () => {
                this.state.isTabActive = false;
                this.logViolation('window_blur');
            });

            window.addEventListener('focus', () => {
                this.state.isTabActive = true;
            });
        },

        /**
         * Prevent page unload/navigation
         */
        setupPageUnloadProtection: function() {
            window.addEventListener('beforeunload', (e) => {
                // Check if exam is still in progress
                const examForm = document.getElementById('exam-form');
                if (examForm) {
                    e.preventDefault();
                    e.returnValue = 'Anda masih mengerjakan ujian. Yakin ingin keluar?';
                    return e.returnValue;
                }
            });

            // Block navigation via links (except submit buttons)
            document.addEventListener('click', (e) => {
                const target = e.target.closest('a');
                if (target && !target.id.includes('submit') && !target.classList.contains('exam-allowed')) {
                    const examForm = document.getElementById('exam-form');
                    if (examForm && !confirm('Anda sedang mengerjakan ujian. Yakin ingin meninggalkan halaman?')) {
                        e.preventDefault();
                        this.logViolation('attempted_navigation');
                    }
                }
            });
        },

        /**
         * Block copy-paste operations
         */
        setupCopyPasteBlocking: function() {
            if (!this.config.enableCopyPasteBlock) return;

            const events = ['copy', 'cut', 'paste'];
            events.forEach(event => {
                document.addEventListener(event, (e) => {
                    e.preventDefault();
                    this.showWarning('❌ Copy-Paste dilarang selama ujian', 'error', 2000);
                    this.logViolation(`attempt_${event}`);
                });
            });

            // Also block via context menu
            document.addEventListener('contextmenu', (e) => {
                if (e.target.closest('.question-card')) {
                    e.preventDefault();
                    return false;
                }
            });
        },

        /**
         * Block right-click context menu
         */
        setupRightClickBlocking: function() {
            if (!this.config.enableRightClickBlock) return;

            document.addEventListener('contextmenu', (e) => {
                const examArea = e.target.closest('#exam-form') || e.target.closest('#question-container');
                if (examArea) {
                    e.preventDefault();
                    this.showWarning('❌ Right-click dilarang selama ujian', 'error', 2000);
                    this.logViolation('right_click');
                    return false;
                }
            });
        },

        /**
         * Detect developer tools opening
         */
        setupDevToolsDetection: function() {
            if (!this.config.enableDevToolDetection) return;

            // Detect F12, Ctrl+Shift+I, Ctrl+Shift+C, Ctrl+Shift+J
            document.addEventListener('keydown', (e) => {
                // F12
                if (e.key === 'F12') {
                    e.preventDefault();
                    this.onDevToolsDetected();
                    return false;
                }

                // Ctrl+Shift+I (Inspect)
                if (e.ctrlKey && e.shiftKey && e.key === 'I') {
                    e.preventDefault();
                    this.onDevToolsDetected();
                    return false;
                }

                // Ctrl+Shift+C (Inspect Element)
                if (e.ctrlKey && e.shiftKey && e.key === 'C') {
                    e.preventDefault();
                    this.onDevToolsDetected();
                    return false;
                }

                // Ctrl+Shift+J (Console)
                if (e.ctrlKey && e.shiftKey && e.key === 'J') {
                    e.preventDefault();
                    this.onDevToolsDetected();
                    return false;
                }

                // Ctrl+Shift+K (Console)
                if (e.ctrlKey && e.shiftKey && e.key === 'K') {
                    e.preventDefault();
                    this.onDevToolsDetected();
                    return false;
                }
            });

            // Detect if DevTools is open by checking window size changes
            const checkDevTools = () => {
                const devToolsThreshold = 160;
                const heightDifference = window.outerHeight - window.innerHeight > devToolsThreshold;
                const widthDifference = window.outerWidth - window.innerWidth > devToolsThreshold;

                if (heightDifference || widthDifference) {
                    this.onDevToolsDetected();
                }
            };

            setInterval(checkDevTools, 1000);
        },

        /**
         * Handle developer tools detection
         */
        onDevToolsDetected: function() {
            if (this.state.devToolsDetected) return; // Already detected

            this.state.devToolsDetected = true;
            this.logViolation('dev_tools_detected');
            this.showWarning('❌ Developer Tools dilarang selama ujian!', 'critical', 5000);

            console.warn('Developer Tools terdeteksi dan dilarang selama ujian');
        },

        /**
         * Block keyboard shortcuts
         */
        setupKeyboardShortcuts: function() {
            document.addEventListener('keydown', (e) => {
                const shortcuts = [
                    { ctrl: true, key: 'S' }, // Ctrl+S (Save)
                    { ctrl: true, key: 'P' }, // Ctrl+P (Print)
                    { ctrl: true, key: 'A' }, // Ctrl+A (Select All)
                    { key: 'PrintScreen' }    // Print Screen
                ];

                for (const shortcut of shortcuts) {
                    let matched = false;

                    if (shortcut.key === 'PrintScreen' && e.key === 'PrintScreen') {
                        matched = true;
                    } else if (shortcut.ctrl && e.ctrlKey && e.key.toUpperCase() === shortcut.key) {
                        matched = true;
                    }

                    if (matched) {
                        e.preventDefault();
                        this.showWarning('❌ Shortcut ini dilarang selama ujian', 'error', 2000);
                        this.logViolation(`shortcut_${e.key}`);
                        return false;
                    }
                }
            });
        },

        /**
         * Prompt fullscreen mode
         */
        setupFullscreenPrompt: function() {
            if (!this.config.enableFullscreen) return;

            const promptFullscreen = () => {
                const fullscreenPrompt = document.createElement('div');
                fullscreenPrompt.innerHTML = `
                    <div style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 9999; font-family: Arial, sans-serif;">
                        <div style="background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; max-width: 500px;">
                            <h2 style="margin-top: 0; color: #333;">🖥️ Masuk Ke Mode Fullscreen</h2>
                            <p style="color: #666; margin: 15px 0;">Untuk keamanan ujian, disarankan menggunakan mode fullscreen. Ini akan menyembunyikan toolbar browser.</p>
                            <div style="display: flex; gap: 10px; justify-content: center; margin-top: 20px;">
                                <button id="fullscreen-yes" style="padding: 10px 20px; background: #3b82f6; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold;">Ya, Masuk Fullscreen</button>
                                <button id="fullscreen-no" style="padding: 10px 20px; background: #6b7280; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold;">Nanti Saja</button>
                            </div>
                        </div>
                    </div>
                `;

                document.body.appendChild(fullscreenPrompt);

                document.getElementById('fullscreen-yes').addEventListener('click', () => {
                    const elem = document.documentElement;
                    if (elem.requestFullscreen) {
                        elem.requestFullscreen().catch(err => {
                            alert(`Fullscreen tidak tersedia: ${err.message}`);
                        });
                    }
                    fullscreenPrompt.remove();
                });

                document.getElementById('fullscreen-no').addEventListener('click', () => {
                    fullscreenPrompt.remove();
                });
            };

            // Show prompt after 2 seconds
            setTimeout(promptFullscreen, 2000);

            // Monitor fullscreen changes
            document.addEventListener('fullscreenchange', () => {
                this.state.isFullscreen = !!document.fullscreenElement;
                if (!this.state.isFullscreen) {
                    this.logViolation('exited_fullscreen');
                }
            });
        },

        /**
         * Setup inactivity warning
         */
        setupInactivityWarning: function() {
            let lastActivityTime = Date.now();
            const inactivityTimeout = 5 * 60 * 1000; // 5 minutes

            const resetTimer = () => {
                lastActivityTime = Date.now();
            };

            document.addEventListener('mousemove', resetTimer);
            document.addEventListener('keypress', resetTimer);
            document.addEventListener('click', resetTimer);

            setInterval(() => {
                if (Date.now() - lastActivityTime > inactivityTimeout) {
                    this.showWarning('⏱️ Anda sudah tidak aktif selama 5 menit. Aktif kembali!', 'warning', 3000);
                    this.logViolation('inactivity_warning');
                    lastActivityTime = Date.now();
                }
            }, 60000);
        },

        /**
         * Log violation to server
         */
        logViolation: function(violationType) {
            this.state.violations.push({
                type: violationType,
                timestamp: new Date().toISOString(),
                tabSwitches: this.state.tabSwitchCount
            });

            // Send to server via fetch
            const sessionId = this.config.sessionId;
            if (sessionId) {
                fetch(`/exams/api/log-violation/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        session_id: sessionId,
                        violation_type: violationType,
                        tab_switches: this.state.tabSwitchCount
                    })
                }).catch(err => console.log('Could not log violation:', err));
            }
        },

        /**
         * Cancel exam due to violations
         */
        cancelExam: function() {
            const examForm = document.getElementById('exam-form');
            if (examForm) {
                const cancelInput = document.createElement('input');
                cancelInput.type = 'hidden';
                cancelInput.name = 'cancel_exam';
                cancelInput.value = 'on';
                examForm.appendChild(cancelInput);
                examForm.submit();
            }
        },

        /**
         * Show warning notification
         */
        showWarning: function(message, type = 'warning', duration = 3000) {
            const alertBox = document.createElement('div');
            const bgColor = {
                'info': 'rgba(59, 130, 246, 0.9)',
                'warning': 'rgba(245, 158, 11, 0.9)',
                'error': 'rgba(239, 68, 68, 0.9)',
                'critical': 'rgba(220, 38, 38, 0.95)'
            }[type] || 'rgba(107, 114, 128, 0.9)';

            alertBox.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: ${bgColor};
                color: white;
                padding: 15px 20px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                font-weight: bold;
                font-size: 14px;
                z-index: 10000;
                animation: slideIn 0.3s ease-out;
                max-width: 400px;
                word-wrap: break-word;
            `;

            alertBox.textContent = message;
            document.body.appendChild(alertBox);

            if (duration > 0) {
                setTimeout(() => {
                    alertBox.style.animation = 'slideOut 0.3s ease-out';
                    setTimeout(() => alertBox.remove(), 300);
                }, duration);
            }
        },

        /**
         * Show critical warning
         */
        showCriticalWarning: function(title, message, callback) {
            const overlay = document.createElement('div');
            overlay.innerHTML = `
                <div style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.8); display: flex; align-items: center; justify-content: center; z-index: 99999; font-family: Arial, sans-serif;">
                    <div style="background: white; padding: 40px; border-radius: 8px; box-shadow: 0 20px 25px rgba(0,0,0,0.2); text-align: center; max-width: 500px;">
                        <h2 style="margin-top: 0; color: #dc2626; font-size: 24px;">${title}</h2>
                        <p style="color: #666; margin: 15px 0; font-size: 16px;">${message}</p>
                        <button id="critical-ok" style="padding: 12px 30px; background: #dc2626; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 16px;">OK, Mengerti</button>
                    </div>
                </div>
            `;

            document.body.appendChild(overlay);

            document.getElementById('critical-ok').addEventListener('click', () => {
                overlay.remove();
                if (callback) callback();
            });
        },

        /**
         * Get CSRF token
         */
        getCookie: function(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
    };

    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);

    // Export for global use
    window.ExamProctor = ExamProctor;
})();
