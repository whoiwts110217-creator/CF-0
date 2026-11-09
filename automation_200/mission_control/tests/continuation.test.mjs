import test from "node:test";
import assert from "node:assert/strict";
import {CONTINUE_MESSAGE, importConversationIndex, selectionSummary,
  makeCheckpoint, runSerial} from "../continue-control/loop.mjs";

test("index retains only metadata and deduplicates", () => {
  const rows = [{id:"123e4567-e89b-12d3-a456-426614174000", title:"First", mapping:{secret:"not retained"}},
    {id:"123e4567-e89b-12d3-a456-426614174000", title:"Duplicate"},
    {id:"../../other", title:"Invalid"}];
  assert.deepEqual(importConversationIndex(rows), [{
    id:"123e4567-e89b-12d3-a456-426614174000",
    title:"First", selected:true, status:"queued"
  }]);
});
test("serial sends exactly one continue after previous completion", async () => {
  const queue = importConversationIndex([
    {id:"123e4567-e89b-12d3-a456-426614174000",title:"A"},
    {id:"123e4567-e89b-12d3-a456-426614174001",title:"B"}]);
  let inFlight = 0;
  const order = [];
  const result = await runSerial({queue, driver:{async sendAndWait(args) {
    assert.equal(args.text, CONTINUE_MESSAGE);
    inFlight++;
    assert.equal(inFlight, 1);
    order.push(args.chatId);
    await Promise.resolve();
    inFlight--;
    return {status:"completed"};
  }}});
  assert.equal(result.status,"completed");
  assert.equal(result.sent,2);
  assert.deepEqual(order,queue.map(x=>x.id));
});
test("cannot start without a supported executor", async () => {
  await assert.rejects(runSerial({queue:[], driver:null}),/executor/);
});
test("uncertain status blocks later chats and repeat", async () => {
  const queue = importConversationIndex([
    {id:"123e4567-e89b-12d3-a456-426614174000"},
    {id:"123e4567-e89b-12d3-a456-426614174001"}]);
  const result = await runSerial({queue, repeat:true, maxPasses:4,
    driver:{async sendAndWait(){return {status:"rate_limited"};}}});
  assert.equal(result.status,"needs_review");
  assert.equal(result.sent,1);
  assert.equal(queue[0].status,"unknown");
  assert.equal(queue[1].status,"queued");
});
test("owner stop does not start next chat", async () => {
  const controller = new AbortController();
  const queue=importConversationIndex([
    {id:"123e4567-e89b-12d3-a456-426614174000"},
    {id:"123e4567-e89b-12d3-a456-426614174001"}]);
  const result=await runSerial({queue, signal:controller.signal,
    driver:{async sendAndWait(){controller.abort();return {status:"completed"};}}});
  assert.equal(result.status,"stopped");
  assert.equal(result.finished,1);
});
test("bounded repeats and exclusions", async () => {
  const queue=importConversationIndex([{id:"123e4567-e89b-12d3-a456-426614174000"},
    {id:"123e4567-e89b-12d3-a456-426614174001"}]);
  queue[1].selected=false;
  const calls=[];
  const result=await runSerial({queue, repeat:true, maxPasses:3,
    driver:{async sendAndWait({pass}){calls.push(pass);return {status:"completed"};}}});
  assert.deepEqual(calls,[1,2,3]);
  assert.equal(result.finished,3);
  assert.deepEqual(selectionSummary(queue),{total:2,eligible:1,excluded:1});
});
test("checkpoint is schema-marked and local-only",()=>{
  const queue=importConversationIndex([{id:"123e4567-e89b-12d3-a456-426614174000"}]);
  const save=makeCheckpoint({account:"secondary",queue});
  assert.equal(save.schema,"cf0.auto08.private_checkpoint.v1");
  assert.equal(save.queue.length,1);
});
