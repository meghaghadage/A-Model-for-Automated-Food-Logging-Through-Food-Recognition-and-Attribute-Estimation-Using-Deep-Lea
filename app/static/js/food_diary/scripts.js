

(function ($) {

    "use strict";
	
	
	// LAYER SLIDER

	enableLayerSlider();
	
	// SWIPER SLIDER
	
	enableSwiper();
	
	
	
	$('a[href="#"]').on('click', function(event){
		return;
	});
	
	// Play Video
	
	if(isExists('.embed-video')){
		$('.embed-video').embedVideo();
	}
	
	// COUNTDOWN TIME 
	
	countdownTime();
	
	
	$('[data-nav-menu]').on('click', function(event){
		
		var $this = $(this),
			visibleHeadArea = $this.data('nav-menu');
		
		$(visibleHeadArea).toggleClass('visible');
		
	});
	
	
	var winWidth = $(window).width();
	dropdownMenu(winWidth);
	
	$(window).on('resize', function(){
		dropdownMenu(winWidth);
		
	});
	
	// Circular Progress Bar
	
	var isAnimated = false;
	
	$(window).on('scroll', function(){
		if(isExists($('.circliful')) && isElementInViewport($('.circliful')) && !isAnimated){
			$('.circliful').circliful();
			isAnimated = true;
		}
		
	});
	
	
})(jQuery);

function isElementInViewport (el) {

    //special bonus for those using jQuery
    if (typeof jQuery === "function" && el instanceof jQuery) {
        el = el[0];
    }

    var rect = el.getBoundingClientRect();

    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) && /*or $(window).height() */
        rect.right <= (window.innerWidth || document.documentElement.clientWidth) /*or $(window).width() */
    );

}


function enableLayerSlider(){
	
	if(isExists('#slider')){
		
		$('#slider').layerSlider({
			sliderVersion: '6.0.0',
			responsiveUnder: 0,
			maxRatio: 1,
			slideBGSize: 'auto',
			hideUnder: 0,
			hideOver: 100000,
			skin: 'outline',
			thumbnailNavigation: 'disabled',
			
		});
	
	}
	
}

function countdownTime(){
	
	if(isExists('#clock')){
		$('#clock').countdown('2018/01/01', function(event) {
			var $this = $(this).html(event.strftime(''
				+ '<div class="time-sec"><h1>%D</h2> days <h1 class="semicolon">:</h1></div>'
				+ '<div class="time-sec"><h1>%H</h2> hours <h1 class="semicolon">:</h1></div>'
				+ '<div class="time-sec"><h1>%M</h2> minutes <h1 class="semicolon">:</h1></div>'
				+ '<div class="time-sec"><h1>%S</h2> seconds </div>'));
		});
	}
}
function dropdownMenu(winWidth){
	
	if(winWidth > 767){
		
		$('.main-menu li').on('mouseover', function(){
			var $this = $(this),
				menuAnchor = $this.children('a');
				
			menuAnchor.addClass('mouseover');
			
		}).on('mouseleave', function(){
			var $this = $(this),
				menuAnchor = $this.children('a');
				
			menuAnchor.removeClass('mouseover');
		});
		
	}else{
		
		$('.main-menu li > a').on('click', function(){
			
			if($(this).attr('href') == '#') return false;
			if($(this).hasClass('mouseover')){ $(this).removeClass('mouseover'); }
			else{ $(this).addClass('mouseover'); }
			return false;
		});
	}
	
}

function enableSwiper(){
	
	if ( isExists('.swiper-container') ) {
		
		$('.swiper-container').each(function (index) {
			
			var swiperDirection 			= $(this).data('swiper-direction'),
				swiperSlidePerView			= $(this).data('swiper-slides-per-view'),
				swiperBreakpoints			= $(this).data('swiper-breakpoints'),
				swiperSpeed					= $(this).data('swiper-speed'),
				swiperCrossFade				= $(this).data('swiper-crossfade'),
				swiperLoop					= $(this).data('swiper-loop'),
				swiperAutoplay 				= $(this).data('swiper-autoplay'),
				swiperMousewheelControl 	= $(this).data('swiper-wheel-control'),
				swipeSlidesPerview 			= $(this).data('slides-perview'),
				swiperMargin 				= parseInt($(this).data('swiper-margin')),
				swiperSlideEffect 			= $(this).data('slide-effect'),
				swiperAutoHeight 			= $(this).data('autoheight'),
				swiperScrollbar 			= ($(this).data('scrollbar') ? $(this).find('.swiper-scrollbar') : null);
				swiperScrollbar 			= (isExists(swiperScrollbar) ? swiperScrollbar : null);
				
			
			var swiper = new Swiper($(this)[0], {
				pagination			: $(this).find('.swiper-pagination'),
				
				
				slidesPerView		: ( swiperSlidePerView ? swiperSlidePerView : 1 ),
				direction			: ( swiperDirection ? swiperDirection : 'horizontal'),
				loop				: ( swiperLoop ? swiperLoop : false),
				nextButton			: '.swiper-button-next',
				prevButton			: '.swiper-button-prev',
				autoplay			: ( swiperAutoplay ? swiperAutoplay : false),
				paginationClickable	: true,
				spaceBetween		: ( swiperMargin ? swiperMargin : 0),
				mousewheelControl	: ( (swiperMousewheelControl) ? swiperMousewheelControl : false),
				scrollbar			: ( swiperScrollbar ? swiperScrollbar : null ),
				scrollbarHide		: false,
				speed				: ( swiperSpeed ? swiperSpeed : 1000 ),
				autoHeight			: ( (swiperAutoHeight == false) ? swiperAutoHeight : true ),
				effect				: ( swiperSlideEffect ? swiperSlideEffect : 'coverflow' ),
				fade				: { crossFade: swiperCrossFade ? swiperCrossFade : false },
				breakpoints			: {
											1200: { slidesPerView: swiperBreakpoints ? 3 : 1, },
											992: { slidesPerView: swiperBreakpoints ? 2 : 1, },
											580: { slidesPerView: 1, }
											
										},
			});
			
		});
		
	}
}

function isExists(elem){
	if ($(elem).length > 0) { 
		return true;
	}
	return false;
}