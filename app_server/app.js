/*
This is the MexicoEn140 main app.
Its structure/procedure is as follows:

	1. invoke libs
	2. configure express
	3. configure twitter
	4. change in natural/lib/natural/tfidf: WordTokenizer -> RegexpTokenizer, maybe
	5. functions
	6. backend operation twitter collecting || cron || database
	7. routings || passing by index.html plus json in 
	8. app listen

*/


// 1. invoke requirements
var port = (process.env.PORT || 5000),
	express = require('express'),
	twitter = require('twitter');
var cool = require('cool-ascii-faces');
	
// 2. express app basic config
var app = express();
app.use(express.static(__dirname + '/public'));

// 3. twitter API config and object
var config = {
    consumer_key: 'CONSUMER_KEY',
    consumer_secret: 'CONSUMER_SECRET',
    access_token_key: 'TOKEN_KEY',
    access_token_secret: 'TOKEN_SECRET',
    };

var twAPI = new twitter(config);
var lastId, lastTweet;
var data = [];
var params = {}
var thisId;


/*/ 6. collecting and buildng jsons periodically
var job = new cronJob.CronJob({
        cronTime: '00 *2 * * * *',
        onTick: getListHistory("mx140-opinion", function(err, data){
                    console.log ("\n.::Doin the task::.");
                    if(err){
                        console.log("Fallo en getListHistory según el cb:" + err);
                    } else {
                        lastTweet = data[0];
       		            console.log("[created at]: " + lastTweet.created_at + "\t[user]: " + 
                            lastTweet.user.screen_name + "\n[text]: " + lastTweet.text);
                    }
                    console.log(new Date().toISOString() + ' .:ok:. ');
                }),
        start: true,
        timeZone: 'America/Los_Angeles',
    });

job.start();
*/



// 7. routings
app.get("/", function (req, res) {
    //send "Hello World" to the client as html
    res.send("<h2>Start Here</h2");
}); 

app.get('/cool', function(req, res) {
  res.send(cool());
});

// 8. testing onthefly json transfering
app.get("/last.json", function	(req, res) {    
	jsonObject = lastTweet
    res.json(jsonObject);
    });


// 8. app listening
app.listen(port);
console.log("\t d[-_-]b Up & running on port :: " + port);

// 5. functions
function getListHistory(listname, cb) {
    fetchTL();
    // fetchTL wrapper function declaration
    function fetchTL(lastId) {
        var params = {
            owner_screen_name: 'MX_en140',
            slug: listname,
            count: 200,
            max_id: lastId
        };
        // here it is the real fetch
        twAPI.get('lists/statuses', params, cb_onTL);
        console.log(".:: Task ended ::.");

        // define the callback for the fetched TimeLine
        function cb_onTL(err, chunk) {
            if (err) {
                console.log('[x_x]: fallo en cb_onTL');
                return cb(err);
            }
            // update data and new maxId
            if (data.length) chunk.shift();
            data = data.concat(chunk);
            thisId = parseInt(data[data.length - 1].id_str);
            lastId = thisId;
            console.log("Data updated " + data.length + "\t with " + thisId);
            // if retrieve something
            /*
            if (chunk.length>2) {
                fetchTL(thisId);
            } else {
            */
                return cb(err, data);
            //}
        } // end cb_onTL
    } // end fetchTL
} // end getListHistory
