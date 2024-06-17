const closeElement = document.getElementById('gestureModeChangeNotification');

            const toggleNotification = () => {
                closeElement.classList[closeElement.classList.contains('open') ? 'remove' : 'add']('open');
            }

            const closeNotification = () => {
                closeElement.classList.remove('open')
            }

            const openNotification = () => {
                closeElement.classList.add('open')
            }