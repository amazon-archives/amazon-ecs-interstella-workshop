/**
 * basic load testing script
 *
 */
package advanced

import io.gatling.core.Predef._
import io.gatling.http.Predef._
import scala.concurrent.duration._

class SimulationA extends Simulation {

  val httpConf = http
    .baseURL("http://stack-loadb-1ki8v4xe20kwt-905242917.us-west-2.elb.amazonaws.com") // Here is the root for all relative URLs, insert microservice url
    .acceptHeader("text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8") // Here are the common headers
    .doNotTrackHeader("1")
    .acceptLanguageHeader("en-US,en;q=0.5")
    .acceptEncodingHeader("gzip, deflate")
    .userAgentHeader("Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:16.0) Gecko/20100101 Firefox/16.0")

  val headers_10 = Map("Content-Type" -> "application/x-www-form-urlencoded") // Note the headers specific to a given request

  val scn = scenario("10MixOfRequests") // A scenario is a chain of requests and pauses
    // valid
    .exec(http("request_1")
      .get("/iridium/"))
    .pause(300 milliseconds) // Note that Gatling has recorded real time pauses
    // valid
    .exec(http("request_2")
      .post("/iridium/")
      .body(StringBody("""{"Message": {"iridium": "1"}}""")).asJSON)
    .pause(2)
    // valid
    .exec(http("request_3")
      .get("/magnesite/"))
    .pause(3)
    // valid
    .exec(http("request_4")
      .post("/magnesite/")
      .body(StringBody("""{"Message": {"magnesite": "1"}}""")).asJSON)
    .pause(2)
    // invalid - wrong element in body
    .exec(http("request_5")
      .post("/iridium/")
      .body(StringBody("""{"Message": {"iridium": "1"}}""")).asJSON)
    .pause(670 milliseconds)
    // invalid - wrong element in body
    .exec(http("request_6")
      .post("/magnesite/")
      .body(StringBody("""{"Message": {"iridium": "1"}}""")).asJSON)
    .pause(629 milliseconds)
    // invalid - request to non-existent URL
    .exec(http("request_7")
      .get("/nonexistent/"))
    .pause(734 milliseconds)
    // valid
    .exec(http("request_8")
      .post("/iridium/")
      .body(StringBody("""{"Message": {"iridium": "1"}}""")).asJSON)
    .pause(5)
    // valid
    .exec(http("request_9")
      .post("/magnesite/")
      .body(StringBody("""{"Message": {"iridium": "1"}}""")).asJSON)
    .pause(1)
    // valid
    .exec(http("request_10")
      .post("/iridium/")
      .body(StringBody("""{"iridium": "1"}""")).asJSON)

  // simulate 20 users doing the same sequences
  setUp(scn.inject(atOnceUsers(20)).protocols(httpConf))
}
