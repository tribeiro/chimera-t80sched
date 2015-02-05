
import numpy as np

from t80sched.scheduler.model import (Session, Targets, Program, Projects,
									  Point,BlockPar,BlockConfig,ObsBlock,
									  Expose, PointVerify, AutoFocus)

from chimera.util.enum import Enum
from chimera.core.site import datetimeFromJD
from chimera.util.position import Position
from chimera.util.output import blue, green, red

import logging as log

ScheduleOptions = Enum("HIG","STD")

def ScheduleFunction(opt,*args,**kwargs):

	sAlg = ScheduleOptions[opt]
	
	if sAlg == ScheduleOptions.HIG:

		def high(slotLen=60.):

			# [To be done] Reject objects that are close to the moon
				
			nightstart = kwargs['obsStart']
			nightend   = kwargs['obsEnd']
			site = kwargs['site']
			
			# Creat observation slots.

			obsSlots = np.array(np.arange(nightstart,nightend,slotLen/60./60./24.),
								dtype= [ ('start',np.float),
										 ('end',np.float)  ,
										 ('slotid',np.int) ,
										 ('blockid',np.int)] )

			log.debug('Creating %i observing slots'%(len(obsSlots)))
			
			obsSlots['end'] += slotLen/60./60/24.
			obsSlots['slotid'] = np.arange(len(obsSlots))
			obsSlots['blockid'] = np.zeros(len(obsSlots))-1

			'''
			obsTargets = np.array([],dtype=[('obsblock',ObsBlock),
											('targets',Targets),
											('blockid',np.int)])'''

			#obsBlocks = np.zeros(len(obsSlots))-1
			
			# For each slot select the higher in the sky...
			# [TBD] - avoid moon
			targets = kwargs['query']
			
			radecArray = np.array([Position.fromRaDec(targets[:][0][2].targetRa,
													  targets[:][0][2].targetDec)])

			radecPos = np.array([0])
			
			blockid = targets[:][0][0].blockid
			
			for itr,target in enumerate(targets):
				if blockid != target[0].blockid:
					radecArray =  np.append(radecArray,Position.fromRaDec(target[2].targetRa,
																		 target[2].targetDec))
					blockid = target[0].blockid
					radecPos = np.append(radecPos,itr)

			'''
			radecArray = np.array([Position.fromRaDec(target[2].targetRa,
													 target[2].targetDec) for target in targets])'''
													 
			mask = np.zeros(len(radecArray)) == 0
			#radecPos = np.arange(len(radecArray))
			
			for itr in range(len(obsSlots)):

				# this if is the key to multitarget blocks...
				if obsSlots['blockid'][itr] == -1:
				
					dateTime = datetimeFromJD(obsSlots['start'][itr])
					lst = site.LST_inRads(dateTime) # in radians

					# This loop is reeeealy slow! Must think of a way to speed things up...

					#sitelat = np.sum(np.array([float(tt) / 60.**i for i,tt in enumerate(str(site['latitude']).split(':'))]))
					alt = np.array([float(site.raDecToAltAz(coords,lst).alt) for coords in radecArray])
					
					stg = alt.argmax()
					
					while targets[:][radecPos[stg]][0].blockid in obsSlots['blockid']:
						log.warning('Observing block already scheduled... Should not be available! Looking for another one... Queue may be compromised...')
					
						mask[stg] = False
						stg = alt[mask].argmax()

					# Check if object is far enough from the moon..
					#moonRaDec = site.moonpos(dateTime)
					
					# Check airmass
					airmass = 1./np.cos(np.pi/2.-alt[stg]*np.pi/180.)
					
					if airmass > targets[:][radecPos[stg]][1].maxairmass:
						log.debug('Object too low in the sky, (Alt.=%6.2f) airmass = %5.2f (max = %5.2f)... Skipping this slot..'%(alt[stg],airmass,targets[:][radecPos[stg]][1].maxairmass))
						continue
				
					s_target = targets[:][radecPos[stg]]

					log.info('Slot[%03i]: %s %s (Alt.=%6.2f, airmass=%5.2f)'%(itr+1,s_target[0],s_target[2],alt[stg],airmass))
					
					mask[stg] = False
					radecArray = radecArray[mask]
					radecPos = radecPos[mask]
					mask = mask[mask]
					obsSlots['blockid'][itr] = s_target[0].blockid
					
					
					# Check if this block has more targets...
					secTargets = targets.filter(ObsBlock.blockid == s_target[0].blockid,
												ObsBlock.objid != s_target[0].objid)
					
					if secTargets.count() > 0:
						log.debug(red('Secondary targets not implemented yet...'))
						pass
					
					if len(mask) == 0:
						break
					
					'''
					if not targets[stg][0].blockid in obsTargets['blockid']:
						#log.debug('#%s %i %i %f: lst = %f | ra = %f | scheduled = %i'%(s_target[0].pid,stg,targets[:][stg][0].blockid,obsSlots['start'][itr],lst,s_target[1].targetRa,targets[:][stg][0].scheduled))
						log.info('Slot[%03i]: %s'%(itr+1,s_target[2]))
						
						#obsTargets = np.append( obsTargets, np.array((s_target[0],s_target[1],targets[stg][0].blockid),dtype=[('obsblock',ObsBlock),('targets',Targets),('blockid',np.int)]))
						
						#self.addObservation(s_target[0],obsSlots['start'][itr])
						targets[stg][0].scheduled = True
					
					else:
						log.debug('#Block already scheduled#%s %i %i %f: lst = %f | ra = %f | scheduled = %i'%(s_target[0].pid,stg,targets[stg][0].blockid,obsSlots['start'][itr],lst,s_target[1].targetRa,targets[stg][0].scheduled))
					'''
					#targets = targets.filter(ObsBlock.scheduled == False)
				else:
					log.warning('Observing slot[%i]@%.4f is already filled with block id %i...'%(itr,
																								 obsSlots['start'][itr],
																								 obsSlots['blockid'][itr]))

			return obsSlots

		return high

	if sAlg == ScheduleOptions.STD:

		def std(slotLen=60.):

			# [TBD] Reject objects that are close to the moon

			# Selecting standard stars is not only searching for the higher in that
			# time but select stars than can be observed at 3 or more (nairmass)
			# different airmasses. It is also important to select stars with
			# different colors (but this will be taken care in the future).

			# [TBD] Select by color also
			nightstart = kwargs['obsStart']
			nightend   = kwargs['obsEnd']
			site = kwargs['site']
			targets = kwargs['query']
			# [TBD] Read this parameters from a file
			nstars = 3
			nairmass = 5
			MINALTITUDE = 10.
			MAXAIRMASS = 1./np.cos(np.pi/2.-np.pi/18.)
			
			radecArray = np.array([Position.fromRaDec(targets[:][0][2].targetRa,
										  targets[:][0][2].targetDec)])

			
			# Creat observation slots.
			slotDtype = [ ('start',np.float),
						 ('end',np.float)  ,
						 ('slotid',np.int) ,
						 ('blockid',np.int),
						 ('filled',np.int)]
			obsSlots = np.array([],
								dtype= slotDtype)
										

			blockid = targets[:][0][0].blockid
			radecPos = np.array([0])
			blockidList = np.array([blockid])
			blockDuration = np.array([0]) # store duration of each block
			maxAirmass = np.array([targets[:][0][1].maxairmass]) # store max airmass of each block
			minAirmass = np.array([targets[:][0][1].minairmass]) # store max airmass of each block
			if maxAirmass[0] < 0:
				maxAirmass[0] = MAXAIRMASS
			if minAirmass[0] < 0:
				minAirmass[0] = MAXAIRMASS # ignore minAirmaa if not set
			
			# Get single block ids and determine block duration
			for itr,target in enumerate(targets):
				if blockid != target[0].blockid:
					radecArray =  np.append(radecArray,Position.fromRaDec(target[2].targetRa,
																		 target[2].targetDec))
					blockid = target[0].blockid
					radecPos = np.append(radecPos,itr)
					blockidList = np.append(blockidList,blockid)
					if target[1].maxairmass > 0:
						maxAirmass = np.append(maxAirmass,target[1].maxairmass)
					else:
						maxAirmass = np.append(maxAirmass,
											   MAXAIRMASS)

					if target[1].minairmass > 0:
						minAirmass = np.append(minAirmass,target[1].minairmass)
					else:
						minAirmass = np.append(minAirmass,
											   MAXAIRMASS) # ignored if not set

					blockDuration = np.append(blockDuration,0.)
				
				blockDuration[-1]+=(target[3].exptime*target[3].nexp)

			# Start allocating
			## get lst at meadle of the observing window
			midnight = (nightstart+nightend)/2.
			dateTime = datetimeFromJD(midnight)
			lstmid = site.LST_inRads(dateTime) # in radians

			nalloc = 0 # number of stars allocated
			nblock = 0 # block iterator
			nballoc = 0 # total number of blocks allocated
			
			while nalloc < nstars or nblock < len(radecPos):
				# get airmasses
				olst = np.float(radecArray[nblock].ra)*np.pi/180.*0.999
				maxAltitude = float(site.raDecToAltAz(radecArray[nblock],
													  olst).alt)
				minAM = 1./np.cos(np.pi/2.-maxAltitude*np.pi/180.)
				
				if maxAltitude < MINALTITUDE:
					nblock+=1
					#log.debug('Max altitude %6.2f lower than minimum: %s'%(float(radecArray[nblock].ra),radecArray[nblock]))
					continue
				elif minAM > minAirmass[nblock]:
					nblock+=1
					#log.debug('Min airmass %7.3f higher than minimum: %7.3f'%(minAM,minAirmass[nblock]))
					continue

				# set desired airmasses
				dairMass = np.linspace(minAM,maxAirmass[nblock],nairmass)
				
				# Decide the start and end times for allocation
				start = nightstart
				end = nightend
				
				if olst > lstmid:
					end = midnight+(olst-lstmid)*12./np.pi/24.
				else:
					start = midnight-(lstmid-olst)*12./np.pi/24.
				
				# find times where object is at desired airmasses
				allocateSlot = np.array([],
										dtype= slotDtype)
										
				log.debug('Trying to allocate %s'%(radecArray[nblock]))
				nballoc_tmp = nballoc
				for dam in dairMass:
					
					time = (start+end)/2.
					am = dam+1.
					niter = 0
					while np.abs(am-dam) > 1e-2:
						time = (start+end)/2.
						dateTime = datetimeFromJD(time)
						lst = site.LST_inRads(dateTime) # in radians
						am = Airmass(float(site.raDecToAltAz(radecArray[nblock],
													  lst).alt))
						niter += 1
						if am > dam:
							start = time
						else:
							end = time
						if niter > 100:
							log.error('Could not converge on search for airmass...')
							break

					filled = False
					# Found time, try to allocate
					for islot in range(len(obsSlots)):
						if obsSlots['start'][islot] < time < obsSlots['end'][islot]:
							filled = True
							log.debug('Slot[%i] filled %.3f/%.3f @ %.3f'%(islot,
																		   obsSlots['start'][islot],
																		   obsSlots['end'][islot],
																		    time))
							break
					
					if not filled:
						allocateSlot = np.append(allocateSlot,
												 np.array([(time,
															time+blockDuration[nblock]/60./60./24.,
															nballoc_tmp,
															blockidList[nblock],
															True)],
														  dtype=slotDtype))
						nballoc_tmp+=1
												
					else:
						break

					start = nightstart
					end = nightend
					
					if olst > lstmid:
						end = midnight+(olst-lstmid)*12./np.pi/24.
					else:
						start = midnight-(lstmid-olst)*12./np.pi/24.

				
				if len(allocateSlot) == nairmass:
					log.info('Allocating...')
					obsSlots = np.append(obsSlots,allocateSlot)
					nalloc+=1
					nballoc += nballoc_tmp
				else:
					nballoc_tmp = 0
					log.debug('Failed...')
				nblock+=1
			
			if nalloc < nstars:
				log.warning('Could not find enough stars.. Found %i of %i...'%(nalloc,nstars))
			
			return obsSlots #targets

		
		return std


def Airmass(alt):
	
	return 1./np.cos(np.pi/2.-alt*np.pi/180.)
