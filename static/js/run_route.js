/**
 * run_route.js — Tinder/Bumble-style stacked card swipe for running through a route.
 *
 * Cards are stacked on top of each other. The top card can be swiped left/right
 * to dismiss it and reveal the next card. 2-3 cards behind are visible as a
 * stacked peek so the user can feel how many tricks remain.
 *
 * Supports: touch swipe, mouse drag, keyboard arrows, dot & button nav.
 */
(function () {
    'use strict';

    var viewport     = document.getElementById('ticketViewport');
    var cards        = Array.from(document.querySelectorAll('.ticket-card'));
    var dots         = Array.from(document.querySelectorAll('.ticket-dot'));
    var progressBar  = document.getElementById('progressBar');
    var progressText = document.getElementById('progressText');
    var hintLeft     = document.getElementById('navHintLeft');
    var hintRight    = document.getElementById('navHintRight');
    var popupOverlay = document.getElementById('routeCompleteOverlay');
    var restartBtn   = document.getElementById('popupRestartBtn');
    var closeBtn     = document.getElementById('popupCloseBtn');

    var totalCards   = cards.length;
    var currentIndex = 0;  // index of the top (active) card

    // ---- Stack layout ----

    /** Assign CSS classes to position cards in the stack relative to currentIndex. */
    function layoutStack() {
        for (var i = 0; i < totalCards; i++) {
            var card = cards[i];
            // Remove all position classes
            card.classList.remove('card-0', 'card-1', 'card-2', 'card-3', 'card-hidden', 'card-swiped', 'dragging');
            card.style.transform = '';
            card.style.opacity = '';

            var offset = i - currentIndex;

            if (offset < 0) {
                // Already swiped away
                card.classList.add('card-swiped');
            } else if (offset === 0) {
                card.classList.add('card-0');
            } else if (offset === 1) {
                card.classList.add('card-1');
            } else if (offset === 2) {
                card.classList.add('card-2');
            } else if (offset === 3) {
                card.classList.add('card-3');
            } else {
                card.classList.add('card-hidden');
            }
        }

        // Update dots
        for (var j = 0; j < dots.length; j++) {
            dots[j].classList.remove('active', 'past');
            if (j === currentIndex) {
                dots[j].classList.add('active');
            } else if (j < currentIndex) {
                dots[j].classList.add('past');
            }
        }

        // Update nav hints
        if (hintLeft)  hintLeft.classList.toggle('hidden', currentIndex === 0);
        if (hintRight) hintRight.classList.toggle('hidden', currentIndex === totalCards - 1);

        // Update progress
        var pct = totalCards > 1 ? Math.round((currentIndex / (totalCards - 1)) * 100) : 100;
        if (progressBar)  progressBar.style.width = pct + '%';
        if (progressText) progressText.textContent = (currentIndex + 1) + ' / ' + totalCards;
    }

    /** Show the route complete popup. */
    function showPopup() {
        if (popupOverlay) popupOverlay.classList.add('show');
    }

    /** Hide the route complete popup. */
    function hidePopup() {
        if (popupOverlay) popupOverlay.classList.remove('show');
    }

    /** Animate the top card off-screen, then advance. */
    function swipeCard(direction) {
        if (currentIndex >= totalCards) return;

        var card = cards[currentIndex];
        var xOut = direction === 'left' ? -window.innerWidth : window.innerWidth;

        card.style.transition = 'transform 0.4s ease, opacity 0.4s ease';
        card.style.transform = 'translateX(' + xOut + 'px) rotate(' + (direction === 'left' ? -15 : 15) + 'deg)';
        card.style.opacity = '0';

        var isLast = (currentIndex === totalCards - 1);

        setTimeout(function () {
            card.style.transition = '';
            currentIndex++;
            layoutStack();
            if (isLast) showPopup();
        }, 350);
    }

    /** Go back to the previous card (undo swipe). */
    function unswipeCard() {
        if (currentIndex <= 0) return;
        currentIndex--;
        layoutStack();
    }

    /** Jump directly to a specific card index. */
    function goTo(index) {
        if (index < 0) index = 0;
        if (index >= totalCards) index = totalCards - 1;
        currentIndex = index;
        layoutStack();
    }

    // ---- Touch / mouse drag on the top card ----
    var startX = 0;
    var startY = 0;
    var deltaX = 0;
    var isDragging = false;
    var isScrolling = null;
    var activeCard = null;
    var SWIPE_THRESHOLD = 60;
    var ANGLE_THRESHOLD = 30;

    function onPointerDown(e) {
        if (e.target.closest('a')) return;

        // Only drag the top card
        var topCard = cards[currentIndex];
        if (!topCard) return;

        // Check if the event target is inside the top card
        if (!topCard.contains(e.target) && e.target !== topCard) return;

        var point = e.touches ? e.touches[0] : e;
        startX = point.clientX;
        startY = point.clientY;
        deltaX = 0;
        isDragging = true;
        isScrolling = null;
        activeCard = topCard;
        activeCard.classList.add('dragging');
    }

    function onPointerMove(e) {
        if (!isDragging || !activeCard) return;

        var point = e.touches ? e.touches[0] : e;
        deltaX = point.clientX - startX;
        var deltaY = point.clientY - startY;

        // Decide direction on first significant movement
        if (isScrolling === null && (Math.abs(deltaX) > 5 || Math.abs(deltaY) > 5)) {
            var angle = Math.abs(Math.atan2(deltaY, deltaX) * 180 / Math.PI);
            isScrolling = (angle > 90 - ANGLE_THRESHOLD && angle < 90 + ANGLE_THRESHOLD);
        }

        if (isScrolling) {
            isDragging = false;
            activeCard.classList.remove('dragging');
            activeCard = null;
            return;
        }

        if (e.cancelable) e.preventDefault();

        // Rotate slightly based on drag distance (Tinder effect)
        var rotate = deltaX * 0.08;
        var maxRotate = 20;
        rotate = Math.max(-maxRotate, Math.min(maxRotate, rotate));

        activeCard.style.transform = 'translateX(' + deltaX + 'px) rotate(' + rotate + 'deg)';

        // Fade slightly as card moves away
        var progress = Math.min(Math.abs(deltaX) / (window.innerWidth * 0.4), 1);
        activeCard.style.opacity = String(1 - progress * 0.3);

        // Animate the card behind to "grow" into position as top card moves
        var nextCard = cards[currentIndex + 1];
        if (nextCard) {
            var scale = 0.95 + progress * 0.05;
            var translateY = 12 - progress * 12;
            nextCard.style.transform = 'scale(' + scale + ') translateY(' + translateY + 'px)';
        }
    }

    function onPointerUp() {
        if (!isDragging || !activeCard) return;
        isDragging = false;
        activeCard.classList.remove('dragging');

        if (Math.abs(deltaX) > SWIPE_THRESHOLD) {
            // Swipe away
            var direction = deltaX < 0 ? 'left' : 'right';
            var xOut = direction === 'left' ? -window.innerWidth : window.innerWidth;
            var rotate = direction === 'left' ? -15 : 15;
            var isLast = (currentIndex === totalCards - 1);

            activeCard.style.transition = 'transform 0.35s ease, opacity 0.35s ease';
            activeCard.style.transform = 'translateX(' + xOut + 'px) rotate(' + rotate + 'deg)';
            activeCard.style.opacity = '0';

            var cardRef = activeCard;
            setTimeout(function () {
                cardRef.style.transition = '';
                currentIndex++;
                layoutStack();
                if (isLast) showPopup();
            }, 300);
        } else {
            // Snap back
            activeCard.style.transition = 'transform 0.3s ease, opacity 0.3s ease';
            activeCard.style.transform = 'scale(1) translateY(0) rotate(0deg)';
            activeCard.style.opacity = '1';

            // Reset next card too
            var nextCard = cards[currentIndex + 1];
            if (nextCard) {
                nextCard.style.transition = 'transform 0.3s ease';
                nextCard.style.transform = 'scale(0.95) translateY(12px)';
                setTimeout(function () {
                    nextCard.style.transition = '';
                }, 300);
            }

            setTimeout(function () {
                if (activeCard) activeCard.style.transition = '';
            }, 300);
        }

        activeCard = null;
    }

    // Touch events
    viewport.addEventListener('touchstart', onPointerDown, { passive: true });
    viewport.addEventListener('touchmove', onPointerMove, { passive: false });
    viewport.addEventListener('touchend', onPointerUp);
    viewport.addEventListener('touchcancel', onPointerUp);

    // Mouse events
    viewport.addEventListener('mousedown', onPointerDown);
    document.addEventListener('mousemove', onPointerMove);
    document.addEventListener('mouseup', onPointerUp);

    // ---- Keyboard navigation ----
    document.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
            e.preventDefault();
            swipeCard('left');
        } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
            e.preventDefault();
            unswipeCard();
        }
    });

    // ---- Dot navigation ----
    for (var d = 0; d < dots.length; d++) {
        (function (dot) {
            dot.addEventListener('click', function () {
                var idx = parseInt(dot.getAttribute('data-index'), 10);
                goTo(idx);
            });
        })(dots[d]);
    }

    // ---- Nav hint buttons ----
    if (hintLeft) {
        hintLeft.addEventListener('click', function () { unswipeCard(); });
    }
    if (hintRight) {
        hintRight.addEventListener('click', function () { swipeCard('left'); });
    }

    // ---- Popup buttons ----
    if (restartBtn) {
        restartBtn.addEventListener('click', function () {
            hidePopup();
            goTo(0);
        });
    }
    if (closeBtn) {
        closeBtn.addEventListener('click', function () {
            hidePopup();
        });
    }

    // ---- Initialise ----
    layoutStack();

    // Prevent context menu on long press
    viewport.addEventListener('contextmenu', function (e) {
        e.preventDefault();
    });
})();
