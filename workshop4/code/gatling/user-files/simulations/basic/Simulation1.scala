/**
 * basic load testing script
 *
 */
package basic

import io.gatling.core.Predef._
import io.gatling.http.Predef._
import scala.concurrent.duration._

class Simulation1 extends Simulation {

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
      .get("/iridium/"))
    .pause(2)
    // valid
    .exec(http("request_3")
      .get("/magnesite/"))
    .pause(3)
    // valid
    .exec(http("request_4")
      .get("/magnesite/"))
    .pause(2)
    // invalid - wrong element in body
    .exec(http("request_5")
      .get("/iridium/"))
    .pause(670 milliseconds)
    // invalid - wrong element in body
    .exec(http("request_6")
      .get("/magnesite/"))
    .pause(629 milliseconds)
    // invalid - request to non-existent URL
    .exec(http("request_7")
      .get("/nonexistent/"))
    .pause(734 milliseconds)
    // valid
    .exec(http("request_8")
      .get("/iridium/"))
    .pause(5)
    // valid
    .exec(http("request_9")
      .get("/magnesite/"))
    .pause(1)
    // valid
    .exec(http("request_10")
      .get("/iridium/"))

  // simulate 50 users doing the same sequences
  setUp(scn.inject(atOnceUsers(50)).protocols(httpConf))
}
