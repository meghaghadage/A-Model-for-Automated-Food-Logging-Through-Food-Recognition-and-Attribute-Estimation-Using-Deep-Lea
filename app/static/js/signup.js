(function($) {

    $('.add-info-link ').on('click', function() {
        $('.add_info').toggle( "slow" );
    });

    $('#activity').parent().append('<ul class="list-item" id="newactivity" name="activity"></ul>');
    $('#activity option').each(function(){
        $('#newactivity').append('<li value="' + $(this).val() + '">'+$(this).text()+'</li>');
    });
    $('#activity').remove();
    $('#newactivity').attr('id', 'activity');
    $('#activity li').first().addClass('init');
    $("#activity").on("click", ".init", function() {
        $(this).closest("#activity").children('li:not(.init)').toggle();
    });

    // $('#city').parent().append('<ul class="list-item" id="newcity" name="city"></ul>');
    // $('#city option').each(function(){
    //     $('#newcity').append('<li value="' + $(this).val() + '">'+$(this).text()+'</li>');
    // });
    // $('#city').remove();
    // $('#newcity').attr('id', 'city');
    // $('#city li').first().addClass('init');
    // $("#city").on("click", ".init", function() {
    // $(this).addClass('selected');
    //     $(this).closest("#city").children('li:not(.init)').toggle();
    // });

    var allOptions = $("#activity").children('li:not(.init)');
    $("#activity").on("click", "li:not(.init)", function() {
        allOptions.removeClass('selected');
        $("#activity").children('.init').html($(this).html());
        allOptions.toggle('slow');
    });
    //
    // var FoodOptions = $("#city").children('li:not(.init)');
    // $("#city").on("click", "li:not(.init)", function() {
    //     FoodOptions.removeClass('selected');
    //     $(this).addClass('selected');
    //     $("#city").children('.init').html($(this).html());
    //     FoodOptions.toggle('slow');
    // });

    $('#signup-form').validate({
        rules : {
            userid : {
                required: true,
            },
            name : {
                required: true,
            },
            email : {
                required: true
            },
            password : {
                required: true
            },
            re_password : {
                required: true,
                equalTo: "#password"
            },
            age : {
                required: true,
            },
            height : {
                required: true,
            },
            weight : {
                required: true,
            },
            activity : {
                required: true,
            }
        },
        onfocusout: function(element) {
            $(element).valid();
        },
    });

    jQuery.extend(jQuery.validator.messages, {
        required: "",
        remote: "",
        email: "",
        url: "",
        date: "",
        dateISO: "",
        number: "",
        digits: "",
        creditcard: "",
        equalTo: ""
    });
})(jQuery);
