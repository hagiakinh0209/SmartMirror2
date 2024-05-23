// 2. This code loads the IFrame Player API code asynchronously.
var tag = document.createElement('script');

tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

// 3. This function creates an <iframe> (and YouTube player)
//    after the API code downloads.
var player;
function onYouTubeIframeAPIReady() {

  var ctrlq = document.getElementById("youtube-audio");
  ctrlq.innerHTML = '<img id="youtube-icon" src="" width=40px height=40px/><div id="youtube-player"></div>';
  ctrlq.onclick = toggleAudio;

  player = new YT.Player('youtube-player', {
    height: '0',
    width: '0',
    videoId: ctrlq.dataset.video,
    playerVars: {
      autoplay: ctrlq.dataset.autoplay,
      loop: ctrlq.dataset.loop,
    },
    events: {
      'onReady': onPlayerReady,
      'onStateChange': onPlayerStateChange
    }
  });

  
  function togglePlayButton(play) {
    document.getElementById("youtube-icon").src = play ? "https://i.ibb.co/8K4qvG7/icons8-pause-button-100.png" : "https://www.freeiconspng.com/uploads/play-button-icon-png-15.png";
  }

  function toggleAudio() {
    if (player.getPlayerState() == 1 || player.getPlayerState() == 3) {
      player.pauseVideo();
      togglePlayButton(false);
    } else {
      player.playVideo();
      togglePlayButton(true);
    }
  }

  function onPlayerReady(event) {
    player.setPlaybackQuality("small");
    document.getElementById("youtube-audio").style.display = "block";
    togglePlayButton(player.getPlayerState() !== 5);
  }

  function onPlayerStateChange(event) {
    if (event.data === 0) {
      togglePlayButton(false);
    }
  }
}
