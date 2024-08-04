$(document).ready(function() {
    // Initialize the first tab and pane as active
    $("#groupTab .nav-pills li:first").addClass("active");
    $("#groupTab .tab-pane:first").addClass("active fade in");

    // Show the form group list of the first tab
    $("#groupTab .nav-pills li:first .form-group-list").show();

    // Move forward
    $("#next-tab").on('click', function(e) {
        var $activeTab = $('.dataset-form .nav > .active');
        var $nextTab = $activeTab.next('li');
        
        if ($nextTab.length > 0) {
            $nextTab.find('a').trigger('click');
            // Removed the animate function
            window.scrollTo(0, $nextTab.offset().top);
        }

        // Check if the next tab is the last tab
        if ($nextTab.is(':last-child')) {
            $('#next-tab').hide();
        }

        e.preventDefault();
        return false;
    });

    // Show/hide form group list on tab click
    $(".tab-link").on('click', function(e) {
        var $formGroupList = $(this).siblings(".form-group-list");
        $(".form-group-list").not($formGroupList).slideUp();
        $formGroupList.slideToggle();

        // Scroll to the tab
        var targetTabId = $(this).attr('href');
        $('html, body').animate({
            scrollTop: $(targetTabId).offset().top
        }, 500);

        // Show the next button if not on the last tab
        var $clickedTab = $(this).parent('li');
        if (!$clickedTab.is(':last-child')) {
            $('#next-tab').show();
        }
    });

    // Remove duplicate form groups
    var seenFormGroups = new Set();
    $("#groupTab .tab-pane .card").each(function() {
        var formGroupId = $(this).data("form_group_id");
        if (seenFormGroups.has(formGroupId)) {
            $(this).remove();
        } else {
            seenFormGroups.add(formGroupId);
        }
    });

    // Handle secondary links click
    $(".secondary-link").on('click', function(e) {
        e.preventDefault();
        var targetId = $(this).attr('href');
        var $targetTab = $(targetId).closest('.tab-pane');
        var targetTabId = $targetTab.attr('id');
        
        // Activate the corresponding tab
        $('a[href="#' + targetTabId + '"]').tab('show');
        
        // Scroll to the form group
        $('html, body').animate({
            scrollTop: $(targetId).offset().top
        }, 500);

        // Show the next button if not on the last tab
        var $clickedTab = $('a[href="#' + targetTabId + '"]').parent('li');
        if (!$clickedTab.is(':last-child')) {
            $('#next-tab').show();
        }
    });
});