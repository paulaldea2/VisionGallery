let themeButtons = document.querySelectorAll('.thme-buttons');
themeButtons.forEach(color =>{
    color.addEventListener('click', () =>{
        let dataColor = color.getAttribute('data-color');
        let secColor = color.getAttribute('sec-color');
        document.querySelector(':root').style.setProperty('--main-color', dataColor);
        document.querySelector(':root').style.setProperty('--secondary-color', secColor);
    });
});

onload = function() {
    if ('speechSynthesis' in window) with(speechSynthesis) {

        var playEle = document.querySelector('#play');
        var pauseEle = document.querySelector('#pause');
        var stopEle = document.querySelector('#stop');
        var flag = false;

        playEle.addEventListener('click', onClickPlay);
        pauseEle.addEventListener('click', onClickPause);
        stopEle.addEventListener('click', onClickStop);

        function onClickPlay() {
        if (!flag) {
            flag = true;
            var articles = document.getElementsByTagName('article');
            var texts = "";
            for(var i = 0; i<articles.length; i++){
                var obj = articles[i];
                texts = texts.concat(obj.textContent);
            }
            utterance = new SpeechSynthesisUtterance(texts);
            utterance.voice = getVoices()[0];
            utterance.onend = function() {
            flag = false;
            playEle.className = pauseEle.className = 'button-tts';
            stopEle.className = 'stopped button-tts';
            };
            playEle.className = 'played button-tts';
            stopEle.className = 'button-tts';
            speak(utterance);
        }
        if (paused) { /* unpause/resume narration */
            playEle.className = 'played button-tts';
            pauseEle.className = 'button-tts';
            resume();
        }
        }

        function onClickPause() {
        if (speaking && !paused) { /* pause narration */
            pauseEle.className = 'paused button-tts';
            playEle.className = 'button-tts';
            pause();
        }
        }

        function onClickStop() {
        if (speaking) { /* stop narration */
            /* for safari */
            stopEle.className = 'stopped button-tts';
            playEle.className = pauseEle.className = 'button-tts';
            flag = false;
            cancel();

        }
        }

    }

    else { /* speech synthesis not supported */
        msg = document.createElement('h5');
        msg.textContent = "Detected no support for Speech Synthesis";
        msg.style.textAlign = 'center';
        msg.style.backgroundColor = 'red';
        msg.style.color = 'white';
        msg.style.marginTop = msg.style.marginBottom = 0;
        document.body.insertBefore(msg, document.querySelector('div'));
    }

}