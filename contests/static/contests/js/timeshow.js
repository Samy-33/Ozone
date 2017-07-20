$(document).ready(function(){
//    alert($('#ucont').html());
    $(this).find('div.cont').each(function(){
//        alert($(this).innerHTML);
        $(this).find('span.code').each(function(){
            var str = $(this).html().trim();
            var t = null;
            var ths = $(this);
            $.ajax({
                type:'get',
                url:`/contests/q/${str}/time/`,
                success:function(data){
                    var pre = 'Starts In ';
                    t = data.start;
                    var start = new Date(t);
                    ths.html('');
                    if(start < new Date()){
                        pre = 'Ends In: ';
                        start = new Date(data.end);
                    }
                    if(new Date(data.end) < new Date()){
                        ths.html('Contest Ended');
                        return;
                    }
//                    console.log(start);
                    setInterval(function(){
                        t = new Date();
//                       console.log(ths.html());
//                       console.log(parseInt((start.getTime()-t.getTime())/1000));
                        t = start - t;
                        if(t/(1000*60*60) >= 24){
                            ths.html(`<b>${pre}</b>`+parseInt(t/(1000*60*60*24))+' days');
                        }else{
                            t = t/1000;
                            var hours = parseInt(t/(3600));
                            t -= hours*3600;
                            hours = hours.toString();
                            if(hours.length == 1){
                                hours = '0'+hours;
                            }
                            var mins = parseInt(t/60);
                            t -= mins*60;
                            mins = mins.toString();
                            if(mins.length == 1){
                                mins = '0'+mins;
                            }
                            var secs = parseInt(t);
                            if(secs < 0){
                                location.reload();
                            }
                            secs = secs.toString();
                            if(secs.length == 1){
                                secs = '0'+secs;
                            }
                            ths.html(`<b>${pre}</b>`+ hours+':'+mins+':'+secs);
                        }
                    }, 1000);
                },
                error:function(err){
                    alert('Timer Error');
                }
            });
        });
    });
});
