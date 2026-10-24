// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
contract EcoReviveRegistry {
 address public owner;
 mapping(address=>bool) public authorizedWriters;
 mapping(bytes32=>bool) public registeredProducts;
 mapping(bytes32=>bytes32) public latestPassportHash;
 mapping(bytes32=>uint256) public passportVersion;
 event ProductRegistered(bytes32 indexed productId,bytes32 passportHash,address indexed actor,uint256 timestamp);
 event PassportUpdated(bytes32 indexed productId,uint256 version,bytes32 passportHash,address indexed actor,uint256 timestamp);
 event LifecycleEventRecorded(bytes32 indexed productId,bytes32 indexed eventType,bytes32 evidenceHash,address indexed actor,uint256 timestamp);
 modifier onlyOwner(){require(msg.sender==owner,"owner only");_;}
 modifier onlyWriter(){require(authorizedWriters[msg.sender],"writer not authorized");_;}
 constructor(){owner=msg.sender;authorizedWriters[msg.sender]=true;}
 function setWriter(address writer,bool allowed) external onlyOwner {authorizedWriters[writer]=allowed;}
 function registerProduct(bytes32 productId,bytes32 passportHash) external onlyWriter {
  require(productId!=bytes32(0),"empty product id");require(!registeredProducts[productId],"already registered");
  registeredProducts[productId]=true;latestPassportHash[productId]=passportHash;passportVersion[productId]=1;
  emit ProductRegistered(productId,passportHash,msg.sender,block.timestamp);
 }
 function updatePassport(bytes32 productId,bytes32 passportHash) external onlyWriter {
  require(registeredProducts[productId],"unknown product");latestPassportHash[productId]=passportHash;passportVersion[productId]+=1;
  emit PassportUpdated(productId,passportVersion[productId],passportHash,msg.sender,block.timestamp);
 }
 function recordLifecycleEvent(bytes32 productId,bytes32 eventType,bytes32 evidenceHash) external onlyWriter {
  require(registeredProducts[productId],"unknown product");require(eventType!=bytes32(0),"empty event type");
  emit LifecycleEventRecorded(productId,eventType,evidenceHash,msg.sender,block.timestamp);
 }
 function verifyPassport(bytes32 productId,bytes32 candidateHash) external view returns(bool) {
  return registeredProducts[productId]&&latestPassportHash[productId]==candidateHash;
 }
}